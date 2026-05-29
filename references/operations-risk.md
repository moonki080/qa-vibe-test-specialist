# Operations Risk

Use this reference for production, privileged, broad-impact, migration, or rollback-sensitive changes.

## Risk Dimensions

| Dimension | What to check |
| --- | --- |
| Privileged authority | Role/permission boundary, least privilege, approval path |
| Blast radius | Number of users, records, systems, or workflows affected |
| Reversibility | Rollback, restore point, dry-run, migration down path |
| Observability | Logs, audit trail, correlation IDs, operator visibility |
| Data protection | Personal data, secrets, retention, export, deletion, consent |
| Idempotency | Safe rerun, duplicate request handling, partial failure recovery |
| Timing | Race conditions, scheduled jobs, time zones, retry windows |
| Compatibility | Browser/device, API version, policy, legacy data shape |

## High-Impact Automation Checks

- Permissions are the minimum needed and privileged access is documented.
- Target selection is explicit and testable.
- Scripts support a dry-run, confirmation, or equivalent safe preview mode for broad operations.
- Rollback is defined for configuration, data, permission, scheduled job, and automation changes.
- Audit logs can answer who changed what, when, and for which target.
- Rate limits, throttling, retries, and pagination are handled.
- Cross-system or delegated scenarios do not accidentally affect out-of-scope targets.

## Project Rules File

Before automated remediation, look for `.qa-rules.md` in the target project root. Use it to capture business context that tests may not encode:

- protected business rules and workflows
- auth, role, approval, billing, and data-retention policy
- files or modules that require plan-first review
- commands that are forbidden or require approval
- required sandbox/read-only accounts for external systems

If `.qa-rules.md` is missing for a business-sensitive change, do not infer policy from code alone. Use plan-first mode, document the missing context, and report `Go with caveats` or `No-go` depending on impact.

## Read-Only And Sandbox Rule

For external systems, use read-only credentials or resettable sandbox data unless the user explicitly approves a broader operation. Never use production write/delete credentials for a QA loop without documented scope, rollback, and owner approval.

## Release Gate

Use `No-go` when:

- A privileged operation lacks scope guardrails.
- Rollback is unknown for high-blast-radius changes.
- Tests passed only in local mode while production auth, data, or policy paths differ materially.
- Failure evidence exists but no owner or mitigation is assigned.
- Automated remediation would change policy-sensitive behavior without `.qa-rules.md` context or explicit user approval.

Use `Go with caveats` only when residual risks are explicit, accepted, and monitored.
