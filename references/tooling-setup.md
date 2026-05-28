# Tooling Setup

Use this reference when a test run needs local tools, browser automation, command execution checks, or environment setup guidance.

## Baseline Local Tools

Expected:

- `git` for changed-file and branch context.
- `rg` for fast source search.
- A language runtime matching the project: Node, Python, Go, Rust, .NET, Java, Ruby, PHP, or the project's documented runtime.
- The repository's own package manager and lockfile conventions.

Helpful:

- `gh` for PR and Actions context.
- Docker only when the project already uses it and commands are non-destructive.
- Browser automation tool already present in the project or Codex environment.

## JavaScript / TypeScript

Detection signals:

- `package.json`, lockfiles, Vite/Next/React configs, Playwright/Cypress configs.

Preferred command order:

- Existing scripts: `check`, `test`, `lint`, `typecheck`, `build`, `test:unit`.
- Use the package manager implied by the lockfile: `pnpm`, `yarn`, `bun`, or `npm`.
- For UI/E2E, prefer existing scripts before raw `npx playwright test` or `npx cypress run`.

Do not run dependency installation unless the user explicitly asks.

## Python

Detection signals:

- `pyproject.toml`, `pytest.ini`, `tox.ini`, `setup.cfg`, `requirements.txt`, `tests/`.

Preferred command order:

- Existing project command from docs/config if obvious.
- `python -m pytest` when pytest is configured or tests are pytest-style.
- `python -m unittest discover` for stdlib unittest projects.

## Browser / UI Automation

Use browser automation when the change is user-facing, layout-sensitive, or flow-sensitive.

Evidence to capture:

- Viewport sizes.
- Console errors and failed network responses.
- Screenshots for key states.
- Primary click/keyboard path.
- Responsive overflow or text overlap checks.

Available tools depend on the active Codex environment. Prefer the project-native Playwright/Cypress setup if present. Use Codex browser or computer-use capabilities when the user needs logged-in browser state, local app inspection, or visual screenshots.

## Scripted Automation

Detection signals:

- Shell scripts, task runners, scheduled jobs, broad data updates, permission manifests, or project-specific automation commands.

Preferred checks:

- Use existing dry-run, check, validate, or test modes before broad operations.
- Static review for scope filtering, idempotency, rollback, logging, least privilege, and confirmation prompts.
- Prefer local fixtures, staging data, or disposable test resources before production-impacting operations.

Never run privileged or broad-impact automation against production without explicit user confirmation and a rollback plan.

## Tool Gap Reporting

When a needed tool is missing, report:

- Tool name.
- Why it is needed.
- Command that would be run if available.
- Lowest-risk install or setup path.
- Whether a static fallback was used.

## Secret Handling

- Do not print tokens, cookies, connection strings, service-role keys, service secrets, or personal data in reports.
- Mask sensitive environment variable values.
- Prefer disposable data, local fixtures, and safe non-production environments.
