#!/usr/bin/env python3
"""Detect and run common repository-native QA commands."""

from __future__ import annotations

import argparse
import ast
import json
import os
import shlex
import shutil
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


FAST_NODE_SCRIPTS = ("check", "test", "lint", "typecheck", "build", "build:web", "test:unit")
RELEASE_NODE_SCRIPTS = ("test:e2e", "e2e", "test:integration", "audit")
TEXT_TAIL_LIMIT = 12000
PYTHON_SYNTAX_CHECK = (
    "import ast,pathlib,sys\n"
    "for item in sys.argv[1:]:\n"
    "    path = pathlib.Path(item)\n"
    "    ast.parse(path.read_text(encoding='utf-8'), filename=str(path))\n"
)


@dataclass
class Candidate:
    name: str
    command: list[str]
    reason: str
    mode: str = "smoke"
    category: str = "test"


@dataclass
class Result:
    name: str
    command: str
    reason: str
    category: str
    mode: str
    status: str
    exit_code: int | None
    duration_seconds: float
    stdout_tail: str
    stderr_tail: str


def tail(value: str, limit: int = TEXT_TAIL_LIMIT) -> str:
    if len(value) <= limit:
        return value
    return value[-limit:]


def command_text(command: Iterable[str]) -> str:
    return " ".join(shlex.quote(part) for part in command)


def executable_available(project: Path, command: list[str]) -> bool:
    if not command:
        return False
    executable = command[0]
    if executable.startswith("./") or executable.startswith("../") or os.sep in executable:
        return (project / executable).exists()
    return shutil.which(executable) is not None


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def write_text_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def pick_node_runner(project: Path) -> str:
    if (project / "pnpm-lock.yaml").exists():
        return "pnpm"
    if (project / "yarn.lock").exists():
        return "yarn"
    if (project / "bun.lockb").exists() or (project / "bun.lock").exists():
        return "bun"
    return "npm"


def node_script_command(runner: str, script: str) -> list[str]:
    if runner == "npm":
        return ["npm", "run", script]
    if runner == "pnpm":
        return ["pnpm", "run", script]
    if runner == "yarn":
        return ["yarn", script]
    if runner == "bun":
        return ["bun", "run", script]
    return [runner, "run", script]


def detect_node(project: Path, mode: str, include_audit: bool) -> list[Candidate]:
    package_json = project / "package.json"
    if not package_json.exists():
        return []

    data = read_json(package_json)
    scripts = data.get("scripts") if isinstance(data.get("scripts"), dict) else {}
    runner = pick_node_runner(project)
    candidates: list[Candidate] = []

    for script in FAST_NODE_SCRIPTS:
        if script in scripts:
            category = "build" if script.startswith("build") else "test"
            if script in ("lint", "typecheck"):
                category = script
            candidates.append(
                Candidate(
                    name=f"node:{script}",
                    command=node_script_command(runner, script),
                    reason=f"package.json script '{script}'",
                    mode="smoke" if script in ("check", "test", "build", "build:web") else "standard",
                    category=category,
                )
            )

    if mode == "release":
        for script in RELEASE_NODE_SCRIPTS:
            if script in scripts:
                candidates.append(
                    Candidate(
                        name=f"node:{script}",
                        command=node_script_command(runner, script),
                        reason=f"release-oriented package.json script '{script}'",
                        mode="release",
                        category="e2e" if "e2e" in script else "test",
                    )
                )

    if include_audit and runner == "npm" and (project / "package-lock.json").exists():
        candidates.append(
            Candidate(
                name="node:npm-audit-prod",
                command=["npm", "audit", "--omit=dev", "--audit-level=moderate"],
                reason="package-lock.json present and dependency audit requested",
                mode="release",
                category="security",
            )
        )

    has_playwright = any(project.glob("playwright.config.*"))
    has_cypress = any(project.glob("cypress.config.*"))
    if mode == "release" and has_playwright and not any("playwright" in c.name for c in candidates):
        candidates.append(
            Candidate(
                name="ui:playwright",
                command=["npx", "playwright", "test"],
                reason="playwright.config.* detected",
                mode="release",
                category="e2e",
            )
        )
    if mode == "release" and has_cypress and not any("cypress" in c.name for c in candidates):
        candidates.append(
            Candidate(
                name="ui:cypress",
                command=["npx", "cypress", "run"],
                reason="cypress.config.* detected",
                mode="release",
                category="e2e",
            )
        )

    return candidates


def tests_reference_pytest(tests_dir: Path) -> bool:
    if not tests_dir.exists():
        return False
    for path in tests_dir.rglob("*.py"):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"), filename=str(path))
        except (OSError, SyntaxError):
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                if any(alias.name == "pytest" or alias.name.startswith("pytest.") for alias in node.names):
                    return True
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if module == "pytest" or module.startswith("pytest."):
                    return True
            elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "pytest":
                return True
    return False


def detect_python(project: Path) -> list[Candidate]:
    signals = [
        project / "pyproject.toml",
        project / "pytest.ini",
        project / "tox.ini",
        project / "setup.cfg",
        project / "requirements.txt",
        project / "requirements-dev.txt",
    ]
    tests_dir = project / "tests"
    python_scripts = sorted((project / "scripts").glob("*.py")) if (project / "scripts").exists() else []
    has_python = any(path.exists() for path in signals) or tests_dir.exists() or bool(python_scripts)
    if not has_python:
        return []

    config_text = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore") for path in signals if path.exists()
    )
    candidates: list[Candidate] = []

    if python_scripts:
        candidates.append(
            Candidate(
                name="python:syntax-scripts",
                command=[sys.executable, "-c", PYTHON_SYNTAX_CHECK]
                + [str(path.relative_to(project)) for path in python_scripts],
                reason="Python scripts/*.py detected",
                mode="smoke",
                category="compile",
            )
        )

    if "pytest" in config_text.lower() or tests_reference_pytest(tests_dir):
        candidates.append(
            Candidate(
                name="python:pytest",
                command=[sys.executable, "-m", "pytest"],
                reason="pytest configuration or dependency detected",
                mode="smoke",
                category="test",
            )
        )
    elif tests_dir.exists():
        candidates.append(
            Candidate(
                name="python:unittest",
                command=[sys.executable, "-m", "unittest", "discover", "-s", "tests"],
                reason="tests/ directory detected",
                mode="smoke",
                category="test",
            )
        )
    return candidates


def detect_other(project: Path, mode: str) -> list[Candidate]:
    candidates: list[Candidate] = []

    if (project / "go.mod").exists():
        candidates.append(Candidate("go:test", ["go", "test", "./..."], "go.mod detected"))
    if (project / "Cargo.toml").exists():
        candidates.append(Candidate("rust:cargo-test", ["cargo", "test"], "Cargo.toml detected"))
    if any(project.glob("*.sln")) or any(project.glob("*.csproj")):
        candidates.append(Candidate("dotnet:test", ["dotnet", "test"], ".NET solution/project detected"))
    if (project / "pom.xml").exists():
        candidates.append(Candidate("java:maven-test", ["mvn", "test"], "pom.xml detected"))
    if (project / "gradlew").exists():
        candidates.append(Candidate("java:gradle-test", ["./gradlew", "test"], "gradlew detected"))
    elif (project / "build.gradle").exists() or (project / "build.gradle.kts").exists():
        candidates.append(Candidate("java:gradle-test", ["gradle", "test"], "Gradle build detected"))
    if (project / "composer.json").exists():
        candidates.append(Candidate("php:composer-test", ["composer", "test"], "composer.json detected"))
    if (project / "Gemfile").exists():
        candidates.append(Candidate("ruby:bundle-test", ["bundle", "exec", "rspec"], "Gemfile detected"))

    return candidates


def dedupe(candidates: list[Candidate]) -> list[Candidate]:
    seen: set[str] = set()
    unique: list[Candidate] = []
    for candidate in candidates:
        key = command_text(candidate.command)
        if key in seen:
            continue
        seen.add(key)
        unique.append(candidate)
    return unique


def detect_candidates(project: Path, mode: str, include_audit: bool) -> list[Candidate]:
    candidates: list[Candidate] = []
    candidates.extend(detect_node(project, mode, include_audit))
    candidates.extend(detect_python(project))
    candidates.extend(detect_other(project, mode))

    if mode == "smoke":
        allowed = {"smoke"}
    elif mode == "standard":
        allowed = {"smoke", "standard"}
    else:
        allowed = {"smoke", "standard", "release"}

    return dedupe([candidate for candidate in candidates if candidate.mode in allowed])


def run_candidate(project: Path, candidate: Candidate, timeout: int, dry_run: bool) -> Result:
    started = time.time()
    if dry_run:
        return Result(
            name=candidate.name,
            command=command_text(candidate.command),
            reason=candidate.reason,
            category=candidate.category,
            mode=candidate.mode,
            status="dry-run",
            exit_code=None,
            duration_seconds=0.0,
            stdout_tail="",
            stderr_tail="",
        )

    if not executable_available(project, candidate.command):
        return Result(
            name=candidate.name,
            command=command_text(candidate.command),
            reason=candidate.reason,
            category=candidate.category,
            mode=candidate.mode,
            status="skipped-tool",
            exit_code=None,
            duration_seconds=0.0,
            stdout_tail="",
            stderr_tail=f"Executable not found: {candidate.command[0]}",
        )

    try:
        completed = subprocess.run(
            candidate.command,
            cwd=str(project),
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        status = "pass" if completed.returncode == 0 else "fail"
        return Result(
            name=candidate.name,
            command=command_text(candidate.command),
            reason=candidate.reason,
            category=candidate.category,
            mode=candidate.mode,
            status=status,
            exit_code=completed.returncode,
            duration_seconds=round(time.time() - started, 3),
            stdout_tail=tail(completed.stdout or ""),
            stderr_tail=tail(completed.stderr or ""),
        )
    except subprocess.TimeoutExpired as error:
        return Result(
            name=candidate.name,
            command=command_text(candidate.command),
            reason=candidate.reason,
            category=candidate.category,
            mode=candidate.mode,
            status="timeout",
            exit_code=None,
            duration_seconds=round(time.time() - started, 3),
            stdout_tail=tail((error.stdout or "") if isinstance(error.stdout, str) else ""),
            stderr_tail=tail((error.stderr or "") if isinstance(error.stderr, str) else ""),
        )


def write_markdown(report: dict, path: Path) -> None:
    lines = [
        "# QA Test Runner Evidence",
        "",
        f"- Project: `{report['project']}`",
        f"- Mode: `{report['mode']}`",
        f"- Dry run: `{report['dry_run']}`",
        f"- Summary: {report['summary']['pass']} pass, {report['summary']['fail']} fail, "
        f"{report['summary']['timeout']} timeout, {report['summary']['skipped']} skipped",
        "",
        "## Commands",
        "",
        "| Name | Status | Exit | Duration | Command |",
        "| --- | --- | --- | --- | --- |",
    ]

    for result in report["results"]:
        lines.append(
            "| {name} | {status} | {exit_code} | {duration}s | `{command}` |".format(
                name=result["name"],
                status=result["status"],
                exit_code="" if result["exit_code"] is None else result["exit_code"],
                duration=result["duration_seconds"],
                command=result["command"].replace("|", "\\|"),
            )
        )

    failures = [item for item in report["results"] if item["status"] in {"fail", "timeout", "skipped-tool"}]
    if failures:
        lines.extend(["", "## Failure Evidence", ""])
        for item in failures:
            lines.extend(
                [
                    f"### {item['name']} - {item['status']}",
                    "",
                    f"- Reason: {item['reason']}",
                    f"- Command: `{item['command']}`",
                    f"- Exit code: `{item['exit_code']}`",
                    "",
                ]
            )
            if item["stdout_tail"]:
                lines.extend(["Stdout tail:", "", "```text", item["stdout_tail"].rstrip(), "```", ""])
            if item["stderr_tail"]:
                lines.extend(["Stderr tail:", "", "```text", item["stderr_tail"].rstrip(), "```", ""])

    write_text_file(path, "\n".join(lines).rstrip() + "\n")


def build_summary(results: list[Result]) -> dict:
    return {
        "pass": sum(1 for item in results if item.status == "pass"),
        "fail": sum(1 for item in results if item.status == "fail"),
        "timeout": sum(1 for item in results if item.status == "timeout"),
        "skipped": sum(1 for item in results if item.status == "skipped-tool"),
        "dry_run": sum(1 for item in results if item.status == "dry-run"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect and run repository-native QA commands.")
    parser.add_argument("project", nargs="?", default=".", help="Target project directory")
    parser.add_argument("--mode", choices=("smoke", "standard", "release"), default="smoke")
    parser.add_argument("--command", action="append", default=[], help="Explicit command to run")
    parser.add_argument("--timeout", type=int, default=180, help="Timeout per command in seconds")
    parser.add_argument("--dry-run", action="store_true", help="Detect commands without executing")
    parser.add_argument("--include-audit", action="store_true", help="Include dependency audit commands")
    parser.add_argument("--json-out", help="Write JSON report to this path")
    parser.add_argument("--md-out", help="Write Markdown report to this path")
    args = parser.parse_args()

    project = Path(args.project).expanduser().resolve()
    if not project.exists() or not project.is_dir():
        print(f"Project directory not found: {project}", file=sys.stderr)
        return 2

    candidates = []
    for index, command in enumerate(args.command):
        try:
            command_parts = shlex.split(command)
        except ValueError as error:
            print(f"Invalid --command #{index + 1}: {error}", file=sys.stderr)
            return 2
        if not command_parts:
            print(f"Invalid --command #{index + 1}: command must not be blank", file=sys.stderr)
            return 2
        candidates.append(
            Candidate(
                name=f"custom:{index + 1}",
                command=command_parts,
                reason="explicit --command",
                mode=args.mode,
                category="custom",
            )
        )
    if not candidates:
        candidates = detect_candidates(project, args.mode, args.include_audit)

    results = [run_candidate(project, candidate, args.timeout, args.dry_run) for candidate in candidates]
    report = {
        "project": str(project),
        "mode": args.mode,
        "dry_run": args.dry_run,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "candidate_count": len(candidates),
        "summary": build_summary(results),
        "results": [asdict(item) for item in results],
    }

    output = json.dumps(report, ensure_ascii=False, indent=2)
    print(output)

    if args.json_out:
        write_text_file(Path(args.json_out).expanduser(), output + "\n")
    if args.md_out:
        write_markdown(report, Path(args.md_out).expanduser())

    if any(item.status in {"fail", "timeout"} for item in results):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
