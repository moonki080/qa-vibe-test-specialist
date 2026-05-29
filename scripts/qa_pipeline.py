#!/usr/bin/env python3
"""Run a compact QA evidence pipeline and write a Korean signoff draft."""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
import time
from pathlib import Path


def utc_stamp() -> str:
    return time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())


def script_path(name: str) -> Path:
    return Path(__file__).resolve().with_name(name)


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def command_text(parts: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in parts)


def run_command(parts: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(parts, text=True, capture_output=True, check=False)


def resolve_rules(project: Path, rules_path: str | None) -> dict:
    path = Path(rules_path).expanduser().resolve() if rules_path else project / ".qa-rules.md"
    if not path.exists():
        return {
            "found": False,
            "path": str(path),
            "status": "missing",
            "note": "Business rules were not provided for this QA run.",
        }
    return {
        "found": True,
        "path": str(path),
        "status": "loaded",
        "note": "Business rules file was present and should be reviewed before remediation.",
    }


def recommendation(current_status: str, summary: dict, rules_found: bool, dry_run: bool) -> str:
    if dry_run:
        return "Review only"
    if current_status in {"blocked-missing-tool", "no-candidates", "max-iterations", "repeated-failure"}:
        return "No-go"
    if int(summary.get("fail") or 0) > 0 or int(summary.get("timeout") or 0) > 0:
        return "No-go"
    if int(summary.get("skipped") or 0) > 0:
        return "No-go"
    if current_status == "goal-met" and rules_found:
        return "Go"
    if current_status == "goal-met":
        return "Go with caveats"
    return "Go with caveats"


def build_goal_loop_command(args: argparse.Namespace, project: Path, out_dir: Path) -> list[str]:
    command = [
        sys.executable,
        str(script_path("qa_goal_loop.py")),
        str(project),
        "--goal",
        args.goal,
        "--mode",
        args.mode,
        "--state",
        str(out_dir / "qa-goal-loop.json"),
        "--md-out",
        str(out_dir / "qa-goal-loop.md"),
        "--evidence-dir",
        str(out_dir / "evidence"),
        "--timeout",
        str(args.timeout),
        "--max-iterations",
        str(args.max_iterations),
    ]
    for explicit_command in args.command or []:
        command.extend(["--command", explicit_command])
    if args.include_audit:
        command.append("--include-audit")
    if args.dry_run:
        command.append("--dry-run")
    return command


def build_signoff(
    args: argparse.Namespace,
    project: Path,
    out_dir: Path,
    rules: dict,
    state: dict,
    runner_report: dict,
    remediation_path: Path,
    goal_command: list[str],
    remediation_command: list[str],
) -> str:
    latest = state.get("iterations", [{}])[-1] if state.get("iterations") else {}
    summary = latest.get("summary") or runner_report.get("summary", {})
    current_status = state.get("current_status", "unknown")
    decision = recommendation(current_status, summary, bool(rules.get("found")), args.dry_run)
    failures = latest.get("failures") or [
        item
        for item in runner_report.get("results", [])
        if item.get("status") in {"fail", "timeout", "skipped-tool"}
    ]
    residual_risks = []
    if not rules.get("found"):
        residual_risks.append("`.qa-rules.md`가 없어 비즈니스 규칙과 보호 정책을 확인하지 못했습니다.")
    if args.dry_run:
        residual_risks.append("Dry-run 결과이므로 실제 테스트 실행 증거는 제한적입니다.")
    if not failures and not residual_risks:
        residual_risks.append("현재 자동화 범위 밖의 수동 UI/API/외부 시스템 검증은 별도 확인이 필요할 수 있습니다.")

    lines = [
        "# 자동 QA 실행 보고서",
        "",
        f"- 대상 프로젝트: `{project}`",
        f"- 목표: {args.goal}",
        f"- 모드: `{args.mode}`",
        f"- 현재 상태: `{current_status}`",
        f"- 권고: **{decision}**",
        f"- 최대 반복 제한: {args.max_iterations}",
        f"- 프로젝트 규칙: `{rules.get('status')}` ({rules.get('path')})",
        "",
        "## 실행 명령",
        "",
        f"- Goal loop: `{command_text(goal_command)}`",
        f"- Remediation plan: `{command_text(remediation_command)}`",
        "",
        "## 결과 요약",
        "",
        f"- Pass: {summary.get('pass', 0)}",
        f"- Fail: {summary.get('fail', 0)}",
        f"- Timeout: {summary.get('timeout', 0)}",
        f"- Skipped: {summary.get('skipped', 0)}",
        f"- Dry-run: {summary.get('dry_run', 0)}",
        "",
        "## 결함 및 차단 항목",
        "",
    ]

    if failures:
        for item in failures:
            lines.extend(
                [
                    f"### {item.get('name', 'unknown')} - {item.get('status', '')}",
                    f"- Command: `{item.get('command', '')}`",
                    f"- Reason: {item.get('reason', '')}",
                    f"- Exit code: `{item.get('exit_code', '')}`",
                    "",
                ]
            )
    else:
        lines.extend(["- 자동 실행 범위에서 실패, 타임아웃, skipped-tool 항목은 없습니다.", ""])

    lines.extend(["## 잔여 리스크", ""])
    lines.extend(f"- {item}" for item in residual_risks)
    lines.extend(
        [
            "",
            "## 산출물",
            "",
            f"- Goal loop JSON: `{out_dir / 'qa-goal-loop.json'}`",
            f"- Goal loop Markdown: `{out_dir / 'qa-goal-loop.md'}`",
            f"- Runner evidence JSON: `{latest.get('report_json', '')}`",
            f"- Runner evidence Markdown: `{latest.get('report_md', '')}`",
            f"- Remediation plan: `{remediation_path}`",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run QA evidence, remediation planning, and Korean signoff in one pass.")
    parser.add_argument("project", nargs="?", default=".", help="Target project directory")
    parser.add_argument("--goal", default="Target QA checks pass with no unresolved high-risk findings")
    parser.add_argument("--mode", choices=("smoke", "standard", "release"), default="standard")
    parser.add_argument("--command", action="append", default=[], help="Explicit command to include")
    parser.add_argument("--out-dir", help="Directory for pipeline evidence")
    parser.add_argument("--rules", help="Path to .qa-rules.md or equivalent business rules file")
    parser.add_argument("--timeout", type=int, default=180, help="Timeout per command in seconds")
    parser.add_argument("--max-iterations", type=int, default=3)
    parser.add_argument("--include-audit", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    project = Path(args.project).expanduser().resolve()
    if not project.exists() or not project.is_dir():
        print(f"Project directory not found: {project}", file=sys.stderr)
        return 2

    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else Path("/tmp") / f"qa-vibe-pipeline-{utc_stamp()}"
    out_dir.mkdir(parents=True, exist_ok=True)
    rules = resolve_rules(project, args.rules)

    goal_command = build_goal_loop_command(args, project, out_dir)
    goal_result = run_command(goal_command)
    state_path = out_dir / "qa-goal-loop.json"
    state = read_json(state_path)
    latest = state.get("iterations", [{}])[-1] if state.get("iterations") else {}
    runner_json_text = str(latest.get("report_json", ""))
    runner_json = Path(runner_json_text).expanduser() if runner_json_text else None
    runner_report = read_json(runner_json) if runner_json else {}

    remediation_path = out_dir / "qa-remediation.md"
    remediation_command = [
        sys.executable,
        str(script_path("qa_remediation_plan.py")),
        str(runner_json or ""),
        "--write",
        str(remediation_path),
    ]
    remediation_result = run_command(remediation_command) if runner_json and runner_json.exists() else None

    signoff_path = out_dir / "ko-qa-auto-signoff.md"
    signoff = build_signoff(
        args,
        project,
        out_dir,
        rules,
        state,
        runner_report,
        remediation_path,
        goal_command,
        remediation_command,
    )
    write_text(signoff_path, signoff)

    current_status = state.get("current_status", "unknown")
    summary = latest.get("summary") or runner_report.get("summary", {})
    decision = recommendation(current_status, summary, bool(rules.get("found")), args.dry_run)
    payload = {
        "project": str(project),
        "out_dir": str(out_dir),
        "status": current_status,
        "recommendation": decision,
        "rules": rules,
        "goal_loop_exit_code": goal_result.returncode,
        "remediation_exit_code": None if remediation_result is None else remediation_result.returncode,
        "signoff": str(signoff_path),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))

    if decision == "No-go":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
