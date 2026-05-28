# Reporting

Use concise, evidence-first reporting. Keep defects separate from coverage notes.

## Finding Format

```markdown
### [Severity] Short Title
- Scope: file, flow, endpoint, or screen
- Evidence: command, screenshot, log, failing assertion, or code reference
- Expected: expected behavior
- Actual: observed behavior
- Repro: minimal steps or test command
- Alignment: CSTS/ISTQB/ISO/OWASP tag when useful
- Suggested fix: concrete next action
```

Severity guidance:

- `Blocker`: prevents core workflow, causes data loss/security exposure, or blocks release validation.
- `High`: major user-facing failure, broken integration, broad regression, or likely production incident.
- `Medium`: incorrect edge case, degraded UX, missing validation, incomplete error handling.
- `Low`: minor inconsistency, unclear message, maintainability concern, low-risk missing coverage.

## Test Matrix Format

```markdown
| ID | Risk / Claim | Technique | Test Level | Check | Evidence | Result |
| --- | --- | --- | --- | --- | --- | --- |
| QA-001 | Checkout rejects invalid coupon | ISTQB-EP / ISTQB-BVA | API/E2E | Invalid, expired, max-length coupon | `npm test -- coupon` | Pass |
```

## Intermediate Check Summary

```markdown
**QA Snapshot**
- Scope:
- Highest risks:
- Checks run:
- Findings:
- Tests to add next:
- Residual risk:
```

## Final QA Summary

```markdown
**QA Result**
- Scope:
- Standards alignment:
- Commands run:
- Test matrix:
- Findings:
- Fixed during this pass:
- Not tested / blocked:
- Residual risk:
- Recommendation: Go / No-go / Go with caveats
```

## Defect Report Fields

- Title
- Environment
- Preconditions
- Steps to reproduce
- Expected result
- Actual result
- Frequency
- Severity
- Priority
- Evidence
- Suspected area
- Suggested next check

## Standards Alignment Statement

Use this style in final reports:

"Testing was planned using CSTS/ISTQB-aligned technique selection, ISO/IEC/IEEE 29119-style traceability and reporting, ISO/IEC 25010 quality attributes, and OWASP WSTG categories where security was in scope. This is practical alignment, not a formal certification or conformity assessment."
