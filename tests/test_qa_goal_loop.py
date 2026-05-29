from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, relative_path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {relative_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


goal_loop = load_module("qa_goal_loop", "scripts/qa_goal_loop.py")


class GoalStatusTests(unittest.TestCase):
    def test_empty_candidate_report_requires_explicit_allow_empty(self) -> None:
        report = {"dry_run": False, "candidate_count": 0, "summary": {}}

        self.assertEqual(goal_loop.goal_status(report, allow_empty=False, allow_skipped=False), "no-candidates")
        self.assertEqual(goal_loop.goal_status(report, allow_empty=True, allow_skipped=False), "goal-met")

    def test_skipped_tool_blocks_unless_allowed(self) -> None:
        report = {
            "dry_run": False,
            "candidate_count": 1,
            "summary": {"pass": 0, "fail": 0, "timeout": 0, "skipped": 1},
        }

        self.assertEqual(goal_loop.goal_status(report, allow_empty=False, allow_skipped=False), "blocked-missing-tool")
        self.assertEqual(goal_loop.goal_status(report, allow_empty=False, allow_skipped=True), "goal-met")

    def test_repeated_failure_requires_three_matching_signatures(self) -> None:
        iterations = [
            {"failure_signature": ["test::fail"]},
            {"failure_signature": ["test::fail"]},
            {"failure_signature": ["test::fail"]},
        ]

        self.assertTrue(goal_loop.repeated_failure(iterations))
        self.assertFalse(goal_loop.repeated_failure(iterations[:2]))

    def test_state_compatibility_requires_same_execution_context(self) -> None:
        project = Path("/tmp/project").resolve()
        state = {
            "project": str(project),
            "goal": "checks pass",
            "mode": "smoke",
            "commands": ["npm test"],
        }

        self.assertTrue(goal_loop.state_compatible(state, project, "checks pass", "smoke", ["npm test"]))
        self.assertFalse(goal_loop.state_compatible(state, project, "release pass", "smoke", ["npm test"]))
        self.assertFalse(goal_loop.state_compatible(state, project, "checks pass", "release", ["npm test"]))
        self.assertFalse(goal_loop.state_compatible(state, project, "checks pass", "smoke", ["npm run build"]))


if __name__ == "__main__":
    unittest.main()
