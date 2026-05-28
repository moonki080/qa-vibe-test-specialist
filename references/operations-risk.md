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

## Release Gate

Use `No-go` when:

- A privileged operation lacks scope guardrails.
- Rollback is unknown for high-blast-radius changes.
- Tests passed only in local mode while production auth, data, or policy paths differ materially.
- Failure evidence exists but no owner or mitigation is assigned.

Use `Go with caveats` only when residual risks are explicit, accepted, and monitored.
