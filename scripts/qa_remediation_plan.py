#!/usr/bin/env python3
"""Turn qa_test_runner JSON output into a remediation checklist."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load_report(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SystemExit(f"Could not read runner report: {error}") from error


def write_text_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def classify(result: dict) -> str:
    name = str(result.get("name", "")).lower()
    category = str(result.get("category", "")).lower()
    command = str(result.get("command", "")).lower()

    if result.get("status") == "skipped-tool":
        return "Missing local tool"
    if "lint" in category or "lint" in name or "lint" in command:
        return "Lint/style/static-analysis failure"
    if "type" in category or "typecheck" in name or "tsc" in command:
        return "Type or compile-time contract failure"
    if "build" in category or "build" in name:
        return "Build/package failure"
    if "e2e" in category or "playwright" in command or "cypress" in command:
        return "UI/E2E workflow failure"
    if "security" in category or "audit" in command:
        return "Dependency/security advisory"
    if result.get("status") == "timeout":
        return "Timeout or hanging test"
    return "Behavioral test failure"


def make_plan(report: dict) -> str:
    project = report.get("project", "")
    summary = report.get("summary", {})
    failures = [
        item
        for item in report.get("results", [])
        if item.get("status") in {"fail", "timeout", "skipped-tool"}
    ]

    lines = [
        "# QA Remediation Plan",
        "",
        f"- Project: `{project}`",
        f"- Mode: `{report.get('mode', '')}`",
        f"- Summary: {summary.get('pass', 0)} pass, {summary.get('fail', 0)} fail, "
        f"{summary.get('timeout', 0)} timeout, {summary.get('skipped', 0)} skipped",
        "",
    ]

    if not failures:
        lines.extend(
            [
                "## Status",
                "",
                "No failing, timed out, or skipped-tool checks were found in the runner result.",
                "",
                "## Next Checks",
                "",
                "- Review coverage gaps against changed files and user-visible risks.",
                "- Add focused regression tests for any high-risk area that was only covered by smoke checks.",
                "- Run UI/API exploratory checks if the change is user-facing or integration-heavy.",
            ]
        )
        return "\n".join(lines) + "\n"

    lines.extend(["## Fix Queue", ""])

    for index, item in enumerate(failures, start=1):
        classification = classify(item)
        lines.extend(
            [
                f"### QA-FIX-{index:03d}: {item.get('name', 'unknown')} ({item.get('status')})",
                "",
                f"- Classification: {classification}",
                f"- Command: `{item.get('command', '')}`",
                f"- Exit code: `{item.get('exit_code', '')}`",
                f"- Evidence source: `{item.get('reason', '')}`",
                "",
                "Recommended developer loop:",
                "",
                "1. Re-run the command exactly as shown above.",
                "2. Inspect the first actionable error in stderr/stdout and the related changed files.",
                "3. Patch the smallest product-code or test-code cause.",
                "4. Add or strengthen a focused regression assertion if the failure exposes missing coverage.",
                "5. Re-run this command, then rerun the broader suite/build.",
                "",
            ]
        )

        stderr_tail = str(item.get("stderr_tail", "")).strip()
        stdout_tail = str(item.get("stdout_tail", "")).strip()
        if stderr_tail:
            lines.extend(["Stderr tail:", "", "```text", stderr_tail[-2000:], "```", ""])
        elif stdout_tail:
            lines.extend(["Stdout tail:", "", "```text", stdout_tail[-2000:], "```", ""])

    lines.extend(
        [
            "## Verification Order",
            "",
            "1. Narrow failing command for each fixed item.",
            "2. Related unit/integration tests.",
            "3. Build/type/lint checks.",
            "4. UI/API smoke or E2E checks for user-visible flows.",
            "5. Final QA signoff with residual risks.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a remediation checklist from qa_test_runner JSON.")
    parser.add_argument("report_json", help="Path to qa_test_runner JSON output")
    parser.add_argument("--write", help="Write Markdown plan to this path")
    args = parser.parse_args()

    report = load_report(Path(args.report_json).expanduser())
    markdown = make_plan(report)

    if args.write:
        write_text_file(Path(args.write).expanduser(), markdown)
    else:
        sys.stdout.write(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
