# Test Execution Workflow

Use this reference when the user wants the skill to run tests against a local project, capture evidence, and turn results into developer action.

## Principles

- Prefer repository-native commands over new tooling.
- Do not install dependencies, start cloud deployments, mutate databases, or run destructive scripts unless the user explicitly asks.
- Run the narrowest useful command first, then broaden only when needed.
- Capture command, cwd, exit code, duration, stdout/stderr tail, and skipped checks.
- Treat failed commands as evidence. Inspect the code before recommending or applying a fix.

## Direct Runner

From this skill directory:

```bash
python3 scripts/qa_test_runner.py /path/to/project --mode smoke
```

Common options:

```bash
python3 scripts/qa_test_runner.py /path/to/project --mode standard \
  --json-out /tmp/qa-run.json \
  --md-out /tmp/qa-run.md

python3 scripts/qa_test_runner.py /path/to/project --command "npm test" --command "npm run build"

python3 scripts/qa_test_runner.py /path/to/project --dry-run
```

One-shot evidence pipeline:

```bash
python3 scripts/qa_pipeline.py /path/to/project \
  --mode standard \
  --max-iterations 3 \
  --out-dir /tmp/qa-vibe-pipeline
```

Mode guidance:

- `smoke`: fast compile/import/test/build confidence. Avoid slow E2E by default.
- `standard`: smoke plus common lint/type/build/unit checks.
- `release`: broader build, E2E, audit, integration, and signoff-oriented checks.

## Result To Fix Loop

1. Reproduce: run or rerun the failing command exactly as reported.
2. Localize: inspect the failing test, changed files, logs, configuration, and related runtime code.
3. Classify: defect in product code, defect in test, environment/config issue, flaky timing, or missing dependency.
4. Patch: make the smallest target-project change that addresses the cause.
5. Strengthen: add or update a focused regression test when the failure reveals missing coverage.
6. Verify: rerun the narrow failing command, then the broader suite/build.
7. Report: summarize before/after commands, changed files, residual risks, and any checks not run.

Use the remediation helper after a runner JSON file exists:

```bash
python3 scripts/qa_remediation_plan.py /tmp/qa-run.json --write /tmp/qa-remediation.md
```

## Evidence Tags

- `direct-run`: command executed in the target project.
- `dry-run`: command detected but not executed.
- `skipped-tool`: command skipped because the executable is unavailable.
- `timeout`: command exceeded the configured timeout.
- `manual-followup`: failure requires code review or manual UI/API verification.

## When To Stop And Ask

Ask before continuing when:

- A command would install packages, deploy, migrate, delete data, send email/SMS, or call production APIs.
- Credentials, privileged access, or sensitive test data are needed.
- The likely fix requires changing unrelated architecture or policy.
