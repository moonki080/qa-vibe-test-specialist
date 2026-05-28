# Technique Selection

Choose techniques from observed risk and available evidence, not from habit.

## Fast Selection Matrix

| Risk or Artifact | Preferred Techniques | Typical Evidence |
| --- | --- | --- |
| Ambiguous requirement or spec gap | Static review, checklist review, scenario walk-through | Gap table with cited file/section |
| Input classes, categories, roles, statuses | Equivalence partitioning | Test cases per valid/invalid partition |
| Numeric ranges, dates, lengths, limits | Boundary value analysis | Min, min+1, nominal, max-1, max, out-of-range |
| Business rules with multiple conditions | Decision table testing | Rule table with expected outcomes |
| UI, order, lifecycle, workflow, status changes | State transition testing | State/event matrix and invalid transition checks |
| User journey or acceptance behavior | Use-case/scenario testing | End-to-end scenario with preconditions and assertions |
| Many configuration or feature combinations | Pairwise or combinatorial testing | Covering array or reduced combination set |
| Complex logic, branching, error handling | White-box branch/condition testing | Branch list, missing assertions, coverage delta |
| Data transformation, parsing, serialization | Property-based or metamorphic checks | Invariants, round trips, generated examples |
| AI-generated glue code | Static review, mutation-minded assertion review, error guessing | Hallucinated API calls, weak assertions, dead code |
| API endpoint | Contract/schema, positive/negative, authz/authn, idempotency checks | Request/response examples, status codes, schema validation |
| Persistence, migrations, caching | Data lifecycle and state transition tests | Setup/action/assert cleanup, rollback behavior |
| Security-sensitive surface | OWASP-scoped non-destructive review | Threat-focused checklist, safe repro, config evidence |
| Performance-sensitive path | Smoke load, spike, stress, resource observation | p95/p99 latency, throughput, error rate, resource notes |
| UI layout or interaction | Exploratory session, accessibility smoke, responsive visual checks | Screenshots, viewport list, console errors, keyboard path |

## Vibe-Coding Risk Heuristics

Prioritize these checks for AI-generated or fast-iterated code:

- Build and import sanity: generated files compile, dependencies exist, exports match imports.
- Assertion quality: tests assert behavior, not just existence or snapshots.
- Boundary handling: empty, null, long, unicode, duplicate, missing, malformed, and extreme values.
- Auth boundary: role separation, direct object access, server-side enforcement, token/session expiry.
- Persistence correctness: create/update/delete consistency, transaction failures, stale cache behavior.
- Error states: user-visible errors, retry behavior, partial failure, network failure, timeout.
- Concurrency: double submit, duplicate requests, idempotency, optimistic update rollback.
- UI resilience: small viewport, long text, loading/empty/error states, keyboard navigation.
- Maintainability: duplicated generated logic, unreachable code, unclear ownership, missing seams for tests.

## Minimum Coverage by Mode

`intermediate-check`:

- Build/type/lint or nearest equivalent if cheap.
- One happy-path check for changed behavior.
- Two off-happy-path checks selected from highest risk.
- Static review for generated-code failure modes.

`final-result-check`:

- Existing test suite or targeted subset.
- Technique-backed test matrix for every user-visible claim.
- Negative and boundary cases for inputs.
- Integration or E2E check for the main workflow.
- Residual risk list with explicit untested areas.

`release-signoff`:

- Entry/exit criteria.
- Requirements or claim traceability.
- Severity-ranked defects.
- Test execution evidence and blocked checks.
- Go/no-go recommendation.
