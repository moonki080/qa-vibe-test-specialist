# Goal-Driven QA Loop Example

**Goal:** Standard checks pass, build succeeds, and no high-risk QA findings remain.

## Iteration 1

```bash
python scripts/qa_goal_loop.py /path/to/project \
  --goal "standard checks pass and high-risk findings are fixed" \
  --mode standard \
  --state /tmp/qa-goal-loop.json \
  --md-out /tmp/qa-goal-loop.md
```

Result:

- `npm run check`: Fail
- `npm run build`: Not reached or fail
- Status: `needs-remediation`

Action:

- Inspect first failing assertion.
- Patch the verified product-code cause.
- Add a regression assertion.

## Iteration 2

Run the same command again.

Result:

- `npm run check`: Pass
- `npm run build`: Pass
- Status: `goal-met`

Final QA response:

- Goal status: Met
- Iterations: 2
- Commands passing: `npm run check`, `npm run build`
- Fixed: failing validation branch and regression test
- Residual risk: UI browser flow not checked unless a browser tool is available
