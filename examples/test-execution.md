# Direct Test Execution Example

**Scope:** Local PWA project after a vibe-coding session.

**Command:**

```bash
python scripts/qa_test_runner.py /path/to/project --mode standard \
  --json-out /tmp/qa-run.json \
  --md-out /tmp/qa-run.md
```

**Evidence Summary:**

| Command | Result | Evidence |
| --- | --- | --- |
| `npm run check` | Pass | Smoke output captured in runner JSON |
| `npm run build:web` | Pass | Build completed with exit code 0 |
| Browser smoke | Manual follow-up | Open app, login, enter primary flow, inspect console |

**Remediation Step:**

```bash
python scripts/qa_remediation_plan.py /tmp/qa-run.json --write /tmp/qa-remediation.md
```

**Developer Loop:**

1. Fix failing command causes first.
2. Add focused regression tests for uncovered risk.
3. Rerun the narrow command.
4. Rerun build or standard mode.
5. Attach before/after command evidence to QA signoff.

**Residual Risk:**

- UI/browser checks still require Playwright, Cypress, Codex browser, Chrome, or computer-use tooling.
- Production auth, privileged permissions, and external API behavior require a safe test environment.
