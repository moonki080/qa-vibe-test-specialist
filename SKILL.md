---
name: qa-vibe-test-specialist
description: Standards-aligned software testing support for vibe-coded code, prototypes, PRs, implementation diffs, and intermediate results. Use when Codex needs to assess, design, generate, run, or review tests using CSTS-aligned Korean software testing practice, ISTQB-style test techniques, ISO/IEC/IEEE 29119-informed test process and documentation, ISO/IEC 25010 quality attributes, OWASP WSTG security checks, risk-based testing, exploratory testing, defect reports, QA signoff, direct repository test execution, remediation planning, or iterative test-fix-retest improvement loops until a defined quality goal is reached for AI-generated or fast-iterated software work.
---

# QA Vibe Test Specialist

Apply professional software testing discipline to fast AI-generated work without turning every task into a heavyweight audit. Use risk-based judgment, choose explicit test techniques, collect evidence, and report findings in a form a developer can act on.

## Guardrails

- Treat CSTS, ISTQB, ISO/IEC/IEEE 29119, ISO/IEC 25010, and OWASP WSTG as alignment references, not as a claim of official certification or formal conformity assessment.
- Do not quote or reproduce paid standards or copyrighted certification material. Use practical paraphrases, traceability labels, and links to official sources when the user needs source attribution.
- Prefer repository-native tests, tools, and conventions. Add new frameworks only when the project lacks a viable test surface or the user requests it.
- Distinguish verified evidence from inference. Say when a check was not run, was blocked, or only covered by static analysis.
- Keep scope proportional: intermediate vibe-coding checks should be fast and risk-focused; release signoff should be broader and better documented.
- For automated remediation, load target-project `.qa-rules.md` first when available. Treat missing business rules as residual risk when behavior, permissions, billing, data, or workflow policy could be affected.
- Default automated test-fix-retest work to a maximum of 3 iterations. Stop earlier when the same failure repeats after two focused attempts, required credentials/tools are unavailable, or the fix would require broad policy or architecture decisions.
- Use plan-first mode before editing when `.qa-rules.md` is missing for a business-sensitive change, when the change touches auth/permissions/payments/data deletion/migrations, or when production/external systems may be affected.
- Do not run deploy, migration, destructive, production-write, notification-sending, or broad external-system commands without explicit user confirmation and a rollback or sandbox plan.

## Reference Selection

- Read `references/technique-selection.md` when choosing test techniques, coverage targets, or exploratory charters.
- Read `references/standards-map.md` when the user asks for CSTS/ISTQB/ISO/OWASP traceability or an internationally credible basis.
- Read `references/reporting.md` when producing test plans, test cases, defect reports, or QA signoff summaries.
- Read `references/execution-workflow.md` when the user wants actual test commands run, evidence captured, or test results converted into developer fixes.
- Read `references/iterative-improvement.md` when the user wants Codex to keep testing, patching, and retesting until a goal, acceptance criteria, or release threshold is met.
- Read `references/tooling-setup.md` when tools are missing, browser/UI automation is needed, local command setup is unclear, or the user asks how to configure the environment.
- Read `references/operations-risk.md` for production, privileged, broad-impact, data migration, or rollback-sensitive changes.
- Read target-project `.qa-rules.md` before remediation or auto-run loops when it exists; if it does not exist, record that business context was not verified.
- Use `scripts/qa_test_runner.py` to discover and run repository-native tests when deterministic command detection is useful.
- Use `scripts/qa_remediation_plan.py` to convert a runner JSON result into a patch-oriented remediation checklist before editing the target project.
- Use `scripts/qa_goal_loop.py` to record repeated test iterations, goal status, remaining failures, and next actions across a test-fix-retest cycle.
- Use `scripts/qa_pipeline.py` when the user wants one command to run evidence capture, remediation planning, goal-loop status, and a Korean QA signoff draft.
- Use `assets/templates/` only when the user wants a reusable artifact file.

## Fast Auto Mode

Use this mode when the user asks for `qa-auto-run`, one-shot QA, minimal input, or an end-to-end QA pass:

1. Load `.qa-rules.md` from the target project root if present.
2. Run a baseline using repository-native commands or `scripts/qa_pipeline.py`.
3. If defects are actionable and safe, patch the smallest verified cause and add regression coverage when practical.
4. Rerun the narrow failing check, then the broader goal checks.
5. Repeat at most 3 iterations unless the user explicitly sets a different limit.
6. Stop and report `No-go` or `Blocked` when business rules are missing for sensitive behavior, the same failure repeats, required tools/credentials are unavailable, or execution would touch production/broad-impact systems.
7. Produce a Korean QA signoff when the user wants final output only. Include commands run, files changed, tests added, residual risks, and Go/No-go/Go with caveats.

Suggested one-shot prompt:

```text
$qa-vibe-test-specialist Run qa-auto-run on this project. Use .qa-rules.md if present, keep the remediation loop to max 3 iterations, use plan-first mode for business-sensitive or external-system changes, and finish with a Korean QA signoff.
```

## Workflow

1. Establish scope.
   - Inspect the user request, changed files, requirements, docs, UI flows, API contracts, and existing tests.
   - Classify the task as `intermediate-check`, `final-result-check`, `test-generation`, `test-review`, or `release-signoff`.
   - Build a QA inventory of user-visible claims, changed behaviors, data/state transitions, integrations, and quality attributes that could fail.

2. Assess risk.
   - Rank risks by user impact, defect likelihood, change size, complexity, security/privacy exposure, reversibility, and observability.
   - Give extra attention to AI/vibe-coding failure modes: plausible but nonexistent APIs, unhandled edge cases, incomplete persistence, broken auth boundaries, optimistic happy paths, race conditions, weak validation, visual overlap, dependency drift, and unused generated code.

3. Select techniques.
   - Map each meaningful risk to at least one technique from `references/technique-selection.md`.
   - Prefer a small, explicit mix over generic "test more": static review, equivalence partitioning, boundary value analysis, decision table, state transition, use-case/scenario testing, pairwise, white-box branch/condition checks, property/metamorphic checks, exploratory testing, API contract checks, performance smoke checks, and OWASP-scoped security checks.

4. Execute or design checks.
   - Run existing test/lint/type/build commands when available and relevant.
   - When the target project is local and no explicit command is provided, consider:
     - `python3 scripts/qa_test_runner.py /path/to/project --mode smoke`
     - `python3 scripts/qa_test_runner.py /path/to/project --mode standard --json-out /tmp/qa-run.json --md-out /tmp/qa-run.md`
   - Treat the runner as evidence capture, not as a replacement for engineering judgment. Inspect failures, logs, changed files, and relevant code before proposing fixes.
   - For code changes, add or modify focused tests when the user asked for implementation support or when the repo clearly expects tests.
   - After fixing the target project, rerun the narrow failing command first, then the broader suite or build command. Report before/after evidence.
   - If the user asks to continue until a goal is reached, run an explicit loop:
     1. Capture a baseline with `qa_goal_loop.py` or `qa_test_runner.py`.
     2. Fix the highest-severity or first actionable failure.
     3. Add or strengthen regression coverage for that failure when practical.
     4. Rerun the narrow failing check.
     5. Rerun the broader goal checks.
     6. Repeat until exit criteria pass, a blocker requires user input, or the agreed iteration limit is reached.
   - For auto-run loops, use `max_iterations=3` unless the user explicitly sets another value.
   - For UI work, verify primary flows and responsive states with browser automation or screenshots when available.
   - For APIs, include positive, negative, authorization, validation, idempotency, and contract/schema checks where relevant.
   - For security-sensitive surfaces, keep tests authorized and non-destructive; use OWASP WSTG categories to scope review rather than performing broad attack activity.

5. Report evidence.
   - Lead with defects and risks, ordered by severity.
   - For each finding include: severity, affected file/flow, evidence, reproduction or failing check, expected vs actual behavior, likely cause, and suggested next action.
   - Include the technique or alignment tag when useful, for example `ISTQB-BVA`, `ISO29119-test-design`, `ISO25010-security`, `OWASP-WSTG-authn`.
   - End with commands run, tests added or changed, coverage gaps, and residual risk.

## Output Modes

- `intermediate-check`: brief risk inventory, top findings, fast checks run, next tests to add.
- `final-result-check`: complete test matrix, evidence, pass/fail summary, residual risks.
- `test-generation`: proposed tests plus code changes following repo conventions.
- `test-review`: anti-patterns, missing assertions, flaky-test risks, maintainability issues.
- `test-execution`: direct command discovery/execution evidence, failing commands, logs, and a remediation plan.
- `remediation-loop`: reproduce failing check, isolate cause, patch target project, add/regenerate tests, rerun, and report before/after evidence.
- `goal-driven-qa-loop`: keep iterating through test execution, targeted fixes, regression tests, and retesting until explicit acceptance criteria are met or a stop condition is reached.
- `qa-auto-run`: one-shot diagnosis, bounded remediation, retest, and Korean signoff with `.qa-rules.md` context and safety stop conditions.
- `release-signoff`: standards-aligned test summary with traceability, blockers, non-blocking risks, and go/no-go recommendation.
