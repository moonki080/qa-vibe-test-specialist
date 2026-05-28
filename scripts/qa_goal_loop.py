#!/usr/bin/env python3
"""Record repeated QA test iterations until a goal is reached."""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
import time
from pathlib import Path


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def load_state(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def command_text(parts: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in parts)


def runner_script() -> Path:
    return Path(__file__).resolve().with_name("qa_test_runner.py")


def run_test_runner(args: argparse.Namespace, iteration_json: Path, iteration_md: Path) -> dict:
    command = [
        sys.executable,
        str(runner_script()),
        str(Path(args.project).expanduser().resolve()),
        "--mode",
        args.mode,
        "--timeout",
        str(args.timeout),
        "--json-out",
        str(iteration_json),
        "--md-out",
        str(iteration_md),
    ]

    for explicit_command in args.command or []:
        command.extend(["--command", explicit_command])

    if args.include_audit:
        command.append("--include-audit")

    if args.dry_run:
        command.append("--dry-run")

    completed = subprocess.run(command, text=True, capture_output=True, check=False)

    try:
        report = json.loads(iteration_json.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        report = {
            "project": str(Path(args.project).expanduser().resolve()),
            "mode": args.mode,
            "dry_run": args.dry_run,
            "candidate_count": 0,
            "summary": {
                "pass": 0,
                "fail": 1,
                "timeout": 0,
                "skipped": 0,
                "dry_run": 0,
            },
            "results": [
                {
                    "name": "qa_test_runner",
                    "command": command_text(command),
                    "reason": "runner execution failed before writing JSON",
                    "category": "runner",
                    "mode": args.mode,
                    "status": "fail",
                    "exit_code": completed.returncode,
                    "duration_seconds": 0,
                    "stdout_tail": completed.stdout[-4000:],
                    "stderr_tail": completed.stderr[-4000:],
                }
            ],
        }

    report["runner_exit_code"] = completed.returncode
    report["runner_command"] = command_text(command)
    return report


def failure_signature(report: dict) -> list[str]:
    signature = []
    for result in report.get("results", []):
        if result.get("status") in {"fail", "timeout", "skipped-tool"}:
            signature.append(f"{result.get('name')}::{result.get('command')}::{result.get('status')}")
    return sorted(signature)


def goal_status(report: dict, allow_empty: bool, allow_skipped: bool) -> str:
    summary = report.get("summary", {})
    candidate_count = int(report.get("candidate_count") or 0)

    if report.get("dry_run"):
        return "dry-run"
    if candidate_count == 0 and not allow_empty:
        return "no-candidates"
    if int(summary.get("fail") or 0) > 0:
        return "needs-remediation"
    if int(summary.get("timeout") or 0) > 0:
        return "needs-remediation"
    if int(summary.get("skipped") or 0) > 0 and not allow_skipped:
        return "blocked-missing-tool"
    return "goal-met"


def repeated_failure(iterations: list[dict]) -> bool:
    if len(iterations) < 3:
        return False
    latest = iterations[-1].get("failure_signature") or []
    previous = iterations[-2].get("failure_signature") or []
    before_previous = iterations[-3].get("failure_signature") or []
    return bool(latest and latest == previous == before_previous)


def build_markdown(state: dict) -> str:
    lines = [
        "# QA Goal Loop",
        "",
        f"- Project: `{state.get('project', '')}`",
        f"- Goal: {state.get('goal', '')}",
        f"- Mode: `{state.get('mode', '')}`",
        f"- Status: `{state.get('current_status', '')}`",
        f"- Iterations: {len(state.get('iterations', []))}",
        "",
        "## Iterations",
        "",
        "| Iteration | Status | Pass | Fail | Timeout | Skipped | Report |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]

    for item in state.get("iterations", []):
        summary = item.get("summary", {})
        lines.append(
            "| {iteration} | {status} | {pass_count} | {fail} | {timeout} | {skipped} | `{report}` |".format(
                iteration=item.get("iteration"),
                status=item.get("status"),
                pass_count=summary.get("pass", 0),
                fail=summary.get("fail", 0),
                timeout=summary.get("timeout", 0),
                skipped=summary.get("skipped", 0),
                report=item.get("report_json", ""),
            )
        )

    latest = state.get("iterations", [])[-1] if state.get("iterations") else {}
    failures = latest.get("failures", [])
    if failures:
        lines.extend(["", "## Remaining Failures", ""])
        for failure in failures:
            lines.extend(
                [
                    f"### {failure.get('name', 'unknown')} - {failure.get('status', '')}",
                    "",
                    f"- Command: `{failure.get('command', '')}`",
                    f"- Exit code: `{failure.get('exit_code', '')}`",
                    f"- Reason: {failure.get('reason', '')}",
                    "",
                ]
            )
            stderr_tail = str(failure.get("stderr_tail", "")).strip()
            stdout_tail = str(failure.get("stdout_tail", "")).strip()
            if stderr_tail:
                lines.extend(["```text", stderr_tail[-1600:], "```", ""])
            elif stdout_tail:
                lines.extend(["```text", stdout_tail[-1600:], "```", ""])

    lines.extend(["", "## Next Action", ""])
    status = state.get("current_status")
    if status == "goal-met":
        lines.append("- Produce final QA signoff with commands passing, changes made, and residual risks.")
    elif status == "max-iterations":
        lines.append("- Stop the loop and report the remaining blocker or ask for a broader design decision.")
    elif status == "repeated-failure":
        lines.append("- Same failure repeated. Reinspect root cause before another patch or ask for design input.")
    elif status == "blocked-missing-tool":
        lines.append("- Install/configure the missing tool or switch to a static/manual fallback with explicit risk.")
    elif status == "no-candidates":
        lines.append("- Define explicit commands with `--command` or add repository-native test scripts.")
    else:
        lines.append("- Patch the first actionable failure, add regression coverage when practical, and rerun this loop.")

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one QA goal-loop iteration and update loop state.")
    parser.add_argument("project", help="Target project directory")
    parser.add_argument("--goal", default="Target QA checks pass with no unresolved high-risk findings")
    parser.add_argument("--mode", choices=("smoke", "standard", "release"), default="standard")
    parser.add_argument("--command", action="append", default=[], help="Explicit command to include in the goal")
    parser.add_argument("--state", default="/tmp/qa-goal-loop.json", help="Loop state JSON path")
    parser.add_argument("--md-out", default="/tmp/qa-goal-loop.md", help="Loop Markdown summary path")
    parser.add_argument("--evidence-dir", default="/tmp/qa-goal-loop-evidence", help="Directory for per-iteration runner reports")
    parser.add_argument("--timeout", type=int, default=180, help="Timeout per command in seconds")
    parser.add_argument("--max-iterations", type=int, default=5)
    parser.add_argument("--include-audit", action="store_true")
    parser.add_argument("--allow-empty", action="store_true", help="Allow zero detected commands to count as goal met")
    parser.add_argument("--allow-skipped", action="store_true", help="Allow skipped missing-tool checks to count as goal met")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    project = Path(args.project).expanduser().resolve()
    if not project.exists() or not project.is_dir():
        print(f"Project directory not found: {project}", file=sys.stderr)
        return 2

    state_path = Path(args.state).expanduser()
    md_path = Path(args.md_out).expanduser()
    evidence_dir = Path(args.evidence_dir).expanduser()
    evidence_dir.mkdir(parents=True, exist_ok=True)

    state = load_state(state_path)
    iterations = state.get("iterations") if isinstance(state.get("iterations"), list) else []
    next_iteration = len(iterations) + 1
    iteration_json = evidence_dir / f"iteration-{next_iteration:03d}.json"
    iteration_md = evidence_dir / f"iteration-{next_iteration:03d}.md"

    report = run_test_runner(args, iteration_json, iteration_md)
    status = goal_status(report, args.allow_empty, args.allow_skipped)
    failures = [
        item
        for item in report.get("results", [])
        if item.get("status") in {"fail", "timeout", "skipped-tool"}
    ]

    iteration = {
        "iteration": next_iteration,
        "started_at": report.get("generated_at", utc_now()),
        "recorded_at": utc_now(),
        "status": status,
        "summary": report.get("summary", {}),
        "candidate_count": report.get("candidate_count", 0),
        "report_json": str(iteration_json),
        "report_md": str(iteration_md),
        "runner_command": report.get("runner_command", ""),
        "failure_signature": failure_signature(report),
        "failures": failures,
    }
    iterations.append(iteration)

    current_status = status
    if status not in {"goal-met", "dry-run"}:
        if len(iterations) >= args.max_iterations:
            current_status = "max-iterations"
        elif repeated_failure(iterations):
            current_status = "repeated-failure"

    state = {
        "project": str(project),
        "goal": args.goal,
        "mode": args.mode,
        "commands": args.command,
        "max_iterations": args.max_iterations,
        "current_status": current_status,
        "updated_at": utc_now(),
        "iterations": iterations,
    }

    write_json(state_path, state)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(build_markdown(state), encoding="utf-8")

    print(json.dumps(state, ensure_ascii=False, indent=2))

    if current_status == "goal-met" or current_status == "dry-run":
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
