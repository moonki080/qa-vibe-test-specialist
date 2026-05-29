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
  --max-iterations 8
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
- A fix would require broad unrelated rewrites.
- The iteration limit is reached.
- The user's newest instruction pauses or redirects the work.

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
