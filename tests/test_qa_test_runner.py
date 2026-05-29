from __future__ import annotations

import contextlib
import io
import importlib.util
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


runner = load_module("qa_test_runner", "scripts/qa_test_runner.py")


class PythonDetectionTests(unittest.TestCase):
    def test_unittest_is_detected_when_tests_dir_has_no_pytest_signal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            tests_dir = project / "tests"
            tests_dir.mkdir()
            (tests_dir / "test_sample.py").write_text(
                "import unittest\n\n"
                "class SampleTest(unittest.TestCase):\n"
                "    def test_truth(self):\n"
                "        self.assertTrue(True)\n",
                encoding="utf-8",
            )

            candidates = runner.detect_candidates(project, mode="smoke", include_audit=False)
            names = {candidate.name for candidate in candidates}

            self.assertIn("python:unittest", names)
            self.assertNotIn("python:pytest", names)

    def test_pytest_is_detected_when_project_declares_pytest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / "tests").mkdir()
            (project / "pyproject.toml").write_text(
                "[tool.pytest.ini_options]\n"
                "testpaths = ['tests']\n",
                encoding="utf-8",
            )

            candidates = runner.detect_candidates(project, mode="smoke", include_audit=False)
            names = {candidate.name for candidate in candidates}

            self.assertIn("python:pytest", names)
            self.assertNotIn("python:unittest", names)

    def test_pytest_is_detected_when_tests_import_pytest_without_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            tests_dir = project / "tests"
            tests_dir.mkdir()
            (tests_dir / "test_sample.py").write_text(
                "import pytest\n\n"
                "def test_truth():\n"
                "    assert True\n",
                encoding="utf-8",
            )

            candidates = runner.detect_candidates(project, mode="smoke", include_audit=False)
            names = {candidate.name for candidate in candidates}

            self.assertIn("python:pytest", names)
            self.assertNotIn("python:unittest", names)

    def test_python_script_syntax_check_does_not_create_bytecode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            scripts_dir = project / "scripts"
            scripts_dir.mkdir()
            (scripts_dir / "helper.py").write_text("VALUE = 1\n", encoding="utf-8")

            candidates = runner.detect_candidates(project, mode="smoke", include_audit=False)
            syntax_candidate = next(candidate for candidate in candidates if candidate.name == "python:syntax-scripts")
            result = runner.run_candidate(project, syntax_candidate, timeout=30, dry_run=False)

            self.assertEqual(result.status, "pass")
            self.assertFalse(any(project.rglob("__pycache__")))

    def test_dedupe_uses_shell_quoted_command_text(self) -> None:
        candidates = [
            runner.Candidate("a", ["python", "-m", "unittest"], "first"),
            runner.Candidate("b", ["python", "-m", "unittest"], "duplicate"),
        ]

        unique = runner.dedupe(candidates)

        self.assertEqual([candidate.name for candidate in unique], ["a"])

    def test_blank_explicit_command_returns_usage_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            stderr = io.StringIO()
            with mock.patch.object(sys, "argv", ["qa_test_runner.py", tmp, "--command", ""]):
                with contextlib.redirect_stderr(stderr):
                    self.assertEqual(runner.main(), 2)
            self.assertIn("command must not be blank", stderr.getvalue())

    def test_output_paths_create_parent_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "project"
            project.mkdir()
            scripts_dir = project / "scripts"
            scripts_dir.mkdir()
            (scripts_dir / "helper.py").write_text("VALUE = 1\n", encoding="utf-8")
            json_out = Path(tmp) / "reports" / "nested" / "run.json"
            md_out = Path(tmp) / "reports" / "nested" / "run.md"

            stdout = io.StringIO()
            with mock.patch.object(
                sys,
                "argv",
                [
                    "qa_test_runner.py",
                    str(project),
                    "--mode",
                    "smoke",
                    "--json-out",
                    str(json_out),
                    "--md-out",
                    str(md_out),
                ],
            ):
                with contextlib.redirect_stdout(stdout):
                    self.assertEqual(runner.main(), 0)

            self.assertTrue(json_out.exists())
            self.assertTrue(md_out.exists())


if __name__ == "__main__":
    unittest.main()
