from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, relative_path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {relative_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


remediation = load_module("qa_remediation_plan", "scripts/qa_remediation_plan.py")


class RemediationPlanTests(unittest.TestCase):
    def test_no_failures_returns_next_checks(self) -> None:
        report = {
            "project": "/tmp/project",
            "mode": "smoke",
            "summary": {"pass": 1, "fail": 0, "timeout": 0, "skipped": 0},
            "results": [{"name": "unit", "status": "pass"}],
        }

        plan = remediation.make_plan(report)

        self.assertIn("No failing, timed out, or skipped-tool checks were found", plan)
        self.assertIn("Review coverage gaps", plan)

    def test_classifies_skipped_tool_before_generic_behavior_failure(self) -> None:
        result = {
            "name": "python:pytest",
            "command": "python -m pytest",
            "category": "test",
            "status": "skipped-tool",
        }

        self.assertEqual(remediation.classify(result), "Missing local tool")

    def test_classifies_skipped_lint_tool_as_missing_tool(self) -> None:
        result = {
            "name": "node:lint",
            "command": "npm run lint",
            "category": "lint",
            "status": "skipped-tool",
        }

        self.assertEqual(remediation.classify(result), "Missing local tool")

    def test_failure_plan_includes_command_and_tail_evidence(self) -> None:
        report = {
            "project": "/tmp/project",
            "mode": "standard",
            "summary": {"pass": 0, "fail": 1, "timeout": 0, "skipped": 0},
            "results": [
                {
                    "name": "node:lint",
                    "status": "fail",
                    "command": "npm run lint",
                    "exit_code": 1,
                    "reason": "package.json script 'lint'",
                    "category": "lint",
                    "stderr_tail": "lint failed",
                    "stdout_tail": "",
                }
            ],
        }

        plan = remediation.make_plan(report)

        self.assertIn("QA-FIX-001", plan)
        self.assertIn("Lint/style/static-analysis failure", plan)
        self.assertIn("lint failed", plan)

    def test_write_option_creates_parent_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report_path = Path(tmp) / "run.json"
            out_path = Path(tmp) / "reports" / "nested" / "remediation.md"
            report_path.write_text(
                json.dumps(
                    {
                        "project": "/tmp/project",
                        "mode": "smoke",
                        "summary": {"pass": 1, "fail": 0, "timeout": 0, "skipped": 0},
                        "results": [],
                    }
                ),
                encoding="utf-8",
            )

            with mock.patch.object(
                sys,
                "argv",
                ["qa_remediation_plan.py", str(report_path), "--write", str(out_path)],
            ):
                self.assertEqual(remediation.main(), 0)

            self.assertTrue(out_path.exists())


if __name__ == "__main__":
    unittest.main()
