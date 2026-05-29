# QA Vibe Test Specialist

Find the bugs AI-generated code loves to hide.

`qa-vibe-test-specialist` is a Codex Agent Skill for vibe coders who build fast but do not want to ship broken flows, weak tests, missing edge cases, fake confidence, or "it worked once" prototypes.

Run it on a PR, prototype, generated test suite, half-finished feature, or final release candidate. It gives you a risk-based QA report, concrete test cases, defect findings, test execution evidence, remediation steps, and a go/no-go recommendation using CSTS/ISTQB/ISO/OWASP-aligned testing discipline.

When you want more than a report, it can run a goal-driven loop: test the project, patch the highest-risk failure, add regression coverage, retest, and repeat until the agreed quality goal is met or a real blocker is documented.

## Why Vibe Coders Need This

AI makes software creation faster. It also makes bad confidence faster.

Generated code often looks complete while hiding ordinary but expensive defects:

- missing edge cases
- weak assertions
- fake or mismatched APIs
- broken auth boundaries
- optimistic happy paths
- incomplete persistence
- fragile UI states
- untested error handling
- generated code nobody owns

This skill turns "please test this" into a structured QA pass that tells you what is risky, what was checked, what broke, what evidence exists, and what to fix next.

## What You Get In One Pass

- A risk inventory for the feature, diff, API, screen, or workflow.
- A standards-aligned test matrix with concrete techniques, not vague advice.
- Direct test command discovery and execution against a local project.
- Focused test ideas or test code that fits the repository's existing tools.
- Severity-ranked defect reports with evidence and reproduction steps.
- A remediation loop that turns failing commands into targeted code/test fixes.
- A goal-driven test-fix-retest loop that keeps improving the target project until exit criteria are met.
- A final QA signoff with commands run, coverage gaps, residual risk, and go/no-go recommendation.

## Copy-Paste Prompts

```text
$qa-vibe-test-specialist Review this PR as a 5-minute vibe-coding QA check. Focus on hidden high-risk bugs.
```

```text
$qa-vibe-test-specialist Test the current implementation against the requirements and produce a risk-based test matrix.
```

```text
$qa-vibe-test-specialist Review these AI-generated tests for weak assertions, missing edge cases, and flaky-test risks.
```

```text
$qa-vibe-test-specialist Create a final QA signoff summary with findings, commands run, residual risk, and go/no-go recommendation.
```

```text
$qa-vibe-test-specialist Design CSTS/ISTQB-style test cases for this API, including boundary, decision table, auth, and negative cases.
```

```text
$qa-vibe-test-specialist Run the available tests in this local project, capture evidence, turn failures into a remediation plan, apply safe fixes, and rerun the failing checks.
```

```text
$qa-vibe-test-specialist Keep testing, fixing, adding regression coverage, and retesting this project until standard checks pass and no high-risk QA findings remain.
```

## Example Outputs

- [Intermediate vibe-coding QA check](examples/intermediate-check.md)
- [Risk-based test matrix](examples/test-matrix.md)
- [Actionable defect report](examples/defect-report.md)
- [Final QA signoff](examples/final-signoff.md)
- [Direct test execution evidence](examples/test-execution.md)
- [Goal-driven QA loop](examples/goal-driven-loop.md)

## Standards Without Paperwork

This skill is practically aligned with:

- **CSTS**: Korean software testing professional practice and terminology.
- **ISTQB**: equivalence partitioning, boundary value analysis, decision tables, state transition testing, exploratory testing, defect reporting, and test management concepts.
- **ISO/IEC/IEEE 29119**: test process, test design, documentation, and reporting structure.
- **ISO/IEC 25010**: product quality attributes such as functional suitability, reliability, security, performance, compatibility, maintainability, and interaction capability.
- **OWASP WSTG**: safe, scoped web and API security testing categories.

The point is not to turn your prototype into paperwork. The point is to make fast AI-assisted development testable, reviewable, and less fragile.

This is practical alignment, not an official certification, endorsement, or formal conformity assessment.

## Install

One common local skill directory is `$HOME/.agents/skills`:

```bash
mkdir -p ~/.agents/skills
git clone https://github.com/moonki080/qa-vibe-test-specialist.git ~/.agents/skills/qa-vibe-test-specialist
```

Some local Codex builds still discover user skills from `~/.codex/skills`. If that is how your machine is configured:

```bash
git clone https://github.com/moonki080/qa-vibe-test-specialist.git ~/.codex/skills/qa-vibe-test-specialist
```

Restart Codex after installing so the skill can be discovered.

## Run Tests Directly

The skill includes helper scripts for deterministic evidence capture. They do not install dependencies or intentionally modify target source files; invoked project test commands may still create normal local caches or artifacts.

```bash
cd ~/.agents/skills/qa-vibe-test-specialist
python3 scripts/qa_test_runner.py /path/to/project --mode smoke
```

For a fuller pass:

```bash
python3 scripts/qa_test_runner.py /path/to/project --mode standard \
  --json-out /tmp/qa-run.json \
  --md-out /tmp/qa-run.md

python3 scripts/qa_remediation_plan.py /tmp/qa-run.json --write /tmp/qa-remediation.md
```

## Develop This Skill

This repository uses Python standard-library `unittest` tests for its helper scripts, so contributors can validate the skill without installing third-party packages:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/qa_test_runner.py . --mode smoke
python3 scripts/qa_goal_loop.py . --mode smoke \
  --state /tmp/qa-vibe-goal.json \
  --md-out /tmp/qa-vibe-goal.md \
  --evidence-dir /tmp/qa-vibe-goal-evidence
```

## Iterate Until The Goal Is Met

Use the goal-loop helper when you want the agent to keep improving a local project through repeated test-fix-retest cycles.

```bash
python3 scripts/qa_goal_loop.py /path/to/project \
  --goal "standard checks pass and no high-risk QA findings remain" \
  --mode standard \
  --state /tmp/qa-goal-loop.json \
  --md-out /tmp/qa-goal-loop.md \
  --evidence-dir /tmp/qa-goal-loop-evidence
```

For precise release criteria, pass explicit commands:

```bash
python3 scripts/qa_goal_loop.py /path/to/project \
  --goal "release candidate checks pass" \
  --command "npm test" \
  --command "npm run build" \
  --command "npm run test:e2e" \
  --max-iterations 8
```

The loop state records each iteration. After Codex patches the target project, run the same command again to update evidence and decide whether to continue, stop for a blocker, or produce final QA signoff.

The runner detects common repository-native commands such as:

- `npm run check`, `npm test`, `npm run lint`, `npm run typecheck`, `npm run build`
- `pnpm`, `yarn`, and `bun` script variants
- Python test commands through the active interpreter, such as `python3 -m pytest` and `python3 -m unittest discover`
- `go test ./...`, `cargo test`, `dotnet test`, `mvn test`, Gradle tests
- Playwright/Cypress release checks when config files exist and `--mode release` is used

After failures, the remediation workflow is:

1. Reproduce the failing command.
2. Inspect the first actionable error and related changed files.
3. Patch the smallest product-code or test-code cause.
4. Add or strengthen a regression assertion.
5. Rerun the narrow failing command, then the broader suite/build.
6. Report before/after evidence and residual risk.

## When To Use It

- Before merging an AI-generated PR.
- Before sharing a prototype with users.
- After a long vibe-coding session where many files changed.
- When tests exist but feel shallow.
- When no tests exist and you need the smallest useful test set.
- When you need a QA summary that stakeholders can understand.

## Output Modes

- `intermediate-check`: quick risk inventory, top findings, fast checks, next tests to add.
- `final-result-check`: complete test matrix, evidence, pass/fail summary, residual risks.
- `test-generation`: focused tests that follow the repo's own conventions.
- `test-review`: weak assertions, flaky risks, anti-patterns, and missing coverage.
- `test-execution`: direct command discovery/execution evidence and remediation plan.
- `remediation-loop`: reproduce, fix, add regression coverage, rerun, and sign off.
- `goal-driven-qa-loop`: repeat test execution, targeted fixes, regression tests, and retesting until explicit exit criteria are met.
- `release-signoff`: standards-aligned QA summary with traceability and go/no-go recommendation.

## What's Inside

```text
qa-vibe-test-specialist/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── execution-workflow.md
│   ├── iterative-improvement.md
│   ├── operations-risk.md
│   ├── reporting.md
│   ├── standards-map.md
│   ├── technique-selection.md
│   └── tooling-setup.md
├── scripts/
│   ├── qa_goal_loop.py
│   ├── qa_remediation_plan.py
│   └── qa_test_runner.py
├── tests/
│   ├── test_qa_goal_loop.py
│   ├── test_qa_remediation_plan.py
│   └── test_qa_test_runner.py
├── assets/
│   └── templates/
│       ├── defect-report.md
│       ├── ko-defect-report.md
│       ├── ko-qa-iteration-log.md
│       ├── ko-qa-signoff.md
│       ├── ko-quick-test-plan.md
│       ├── qa-iteration-log.md
│       ├── qa-signoff.md
│       └── quick-test-plan.md
└── examples/
    ├── defect-report.md
    ├── final-signoff.md
    ├── goal-driven-loop.md
    ├── intermediate-check.md
    ├── test-execution.md
    └── test-matrix.md
```

## Designed For

- AI builders
- vibe coders
- QA engineers
- SDETs
- startup builders
- Korean QA practitioners using CSTS as a testing reference
- anyone using Codex to produce or review code quickly

## License

MIT
