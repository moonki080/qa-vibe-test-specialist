# Example: Intermediate Vibe-Coding QA Check

Prompt:

```text
$qa-vibe-test-specialist Review this checkout implementation as a 5-minute vibe-coding QA check. Focus on hidden high-risk bugs.
```

Output shape:

```markdown
**QA Snapshot**
- Scope: checkout form, coupon validation, payment retry, order creation
- Highest risks:
  - Payment retry can double-create orders after a timeout.
  - Coupon validation only runs in the UI, not on the API route.
  - Generated tests assert that buttons render but not that payment state changes correctly.

**Findings**

### [High] Coupon discount can be forged by bypassing the UI
- Scope: `POST /api/checkout`
- Evidence: API accepts `discountAmount` from the request body without server-side recalculation.
- Expected: server derives discount from coupon code and cart state.
- Actual: client-provided discount is trusted.
- Repro: send checkout request with `discountAmount: 9999`.
- Alignment: `ISO25010-security`, `OWASP-WSTG-input`, `ISTQB-EXP`
- Suggested fix: ignore client discount fields and recalculate on the server.

### [Medium] Payment retry has no idempotency guard
- Scope: payment retry flow
- Evidence: retry calls `createOrder()` again with no idempotency key.
- Expected: duplicate submissions resolve to one order.
- Actual: two fast retries can create two pending orders.
- Alignment: `ISTQB-ST`, `ISO25010-reliability`
- Suggested fix: add idempotency key per checkout session and test double-submit behavior.

**Checks run**
- `npm test -- checkout`
- static review of `app/api/checkout/route.ts`
- state transition review for `idle -> paying -> failed -> retrying -> paid`

**Tests to add next**
- API negative test for forged discount fields.
- State transition test for retry after payment timeout.
- E2E double-click submit check.

**Residual risk**
- Payment provider webhook behavior was not validated in this pass.
```
