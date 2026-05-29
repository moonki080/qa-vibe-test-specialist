from __future__ import annotations

import contextlib
import importlib.util
import io
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


pipeline = load_module("qa_pipeline", "scripts/qa_pipeline.py")


class PipelineTests(unittest.TestCase):
    def test_recommendation_is_go_with_caveats_without_rules(self) -> None:
        decision = pipeline.recommendation(
            "goal-met",
            {"pass": 1, "fail": 0, "timeout": 0, "skipped": 0},
            rules_found=False,
            dry_run=False,
        )

        self.assertEqual(decision, "Go with caveats")

    def test_resolve_rules_detects_project_rules_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / ".qa-rules.md").write_text("# QA Rules\n", encoding="utf-8")

            rules = pipeline.resolve_rules(project, None)

            self.assertTrue(rules["found"])
            self.assertEqual(rules["status"], "loaded")

    def test_pipeline_writes_signoff_and_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "project"
            project.mkdir()
            scripts_dir = project / "scripts"
            tests_dir = project / "tests"
            scripts_dir.mkdir()
            tests_dir.mkdir()
            (scripts_dir / "helper.py").write_text("VALUE = 1\n", encoding="utf-8")
            (tests_dir / "test_sample.py").write_text(
                "import unittest\n\n"
                "class SampleTest(unittest.TestCase):\n"
                "    def test_truth(self):\n"
                "        self.assertTrue(True)\n",
                encoding="utf-8",
            )
            out_dir = Path(tmp) / "pipeline-out"
            stdout = io.StringIO()

            with mock.patch.object(
                sys,
                "argv",
                ["qa_pipeline.py", str(project), "--mode", "standard", "--out-dir", str(out_dir)],
            ):
                with contextlib.redirect_stdout(stdout):
                    self.assertEqual(pipeline.main(), 0)

            payload = json.loads(stdout.getvalue())
            signoff = Path(payload["signoff"])

            self.assertTrue((out_dir / "qa-goal-loop.json").exists())
            self.assertTrue((out_dir / "qa-remediation.md").exists())
            self.assertTrue(signoff.exists())
            self.assertIn("Go with caveats", signoff.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
