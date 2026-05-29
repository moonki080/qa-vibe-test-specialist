# Iterative Test-Fix-Retest Improvement

Use this reference when the user wants the agent to keep improving a project until a quality goal is reached.

## Goal Contract

Before the loop starts, make the goal concrete. Use the user's goal if given. If not, infer a conservative default:

- Existing smoke/standard test commands pass.
- Build/type/lint checks pass when present.
- High and Blocker findings are fixed or explicitly accepted.
- A focused regression check exists for each fixed behavioral defect when practical.
- UI/API primary flow evidence exists when the change is user-facing or integration-heavy.

Record the goal in the report. Do not claim completion from a single green command if meaningful risks remain untested.

Read `.qa-rules.md` from the target project root before remediation when it exists. If it is missing and the work may touch business rules, authorization, billing, persistence, external systems, or user-visible policy, use plan-first mode and list missing business context as residual risk.

## Loop

1. Baseline
   - Discover and run relevant commands.
   - Capture failing commands, logs, changed files, screenshots, or API evidence.
   - Use `scripts/qa_goal_loop.py` when a persistent iteration record is useful.

2. Prioritize
   - Fix Blocker/High first.
   - Prefer deterministic failures over broad speculative cleanup.
   - If several failures have the same cause, fix the shared root cause first.

3. Patch
   - Make the smallest repo-local change that addresses the verified cause.
   - Preserve user changes and repository conventions.
   - Add or strengthen a regression test when the failure exposes missing coverage.
   - Do not remove or bypass business rules from `.qa-rules.md`; if the rule conflicts with the apparent fix, stop and ask.

4. Retest
   - Rerun the narrow failing command first.
   - Then rerun the broader goal command set.
   - Update the iteration log with pass/fail evidence.

5. Decide
   - Continue if failures remain and the next action is clear.
   - Stop and ask if credentials, production-impacting actions, destructive migrations, paid services, or ambiguous requirements block progress.
   - Stop with `No-go` if the goal cannot be met within the agreed constraints.

## qa_goal_loop.py

Run one recorded iteration:

```bash
python3 scripts/qa_goal_loop.py /path/to/project \
  --goal "standard tests and build pass with no high-risk QA findings" \
  --mode standard \
  --state /tmp/qa-goal-loop.json \
  --md-out /tmp/qa-goal-loop.md
```

Use explicit commands for a precise goal:

```bash
python3 scripts/qa_goal_loop.py /path/to/project \
  --goal "release candidate checks pass" \
  --command "npm test" \
  --command "npm run build" \
  --command "npm run test:e2e" \
  --max-iterations 3
```

After patching the target project, rerun the same `qa_goal_loop.py` command. The state file accumulates iteration history only when the project, goal, mode, and explicit command list match the existing state.

## Exit Criteria

Goal met when:

- All required commands pass.
- No required tool is skipped.
- No command times out.
- Required UI/API/manual checks are either passed or explicitly documented as accepted residual risk.
- The final report includes commands run, changed files, tests added, and residual risks.

## Stop Conditions

Stop the loop and report clearly when:

- The same failure repeats after two focused patches and needs deeper design input.
- A required test depends on missing credentials, production data, paid services, or admin privileges.
- `.qa-rules.md` is missing or conflicts with the proposed fix for business-sensitive behavior.
- The next action would deploy, migrate, delete data, send notifications, charge money, or write to a production/external system without explicit approval.
- A fix would require broad unrelated rewrites.
- The iteration limit is reached.
- The user's newest instruction pauses or redirects the work.

## qa_pipeline.py

Use the pipeline helper when the user wants one command for evidence capture, remediation planning, goal-loop state, and a Korean signoff draft:

```bash
python3 scripts/qa_pipeline.py /path/to/project \
  --mode standard \
  --max-iterations 3 \
  --out-dir /tmp/qa-vibe-pipeline
```

The pipeline does not edit source code. It reduces manual steps and writes the evidence files an agent should inspect before any patch loop.

## Reporting Shape

Use this compact form during the loop:

```markdown
**Iteration N**
- Goal:
- Commands:
- Result:
- Fixed:
- Tests added:
- Remaining failures:
- Next action:
```

Final response:

- Goal status: Met / Not met / Met with caveats.
- Iterations run.
- Commands now passing.
- Changes made.
- Residual risk and untested areas.
