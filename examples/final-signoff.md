# Example: Final QA Signoff

```markdown
**QA Result**
- Scope: checkout, coupon validation, payment retry, order creation, mobile checkout layout
- Standards alignment: CSTS/ISTQB-aligned technique selection, ISO/IEC/IEEE 29119-style reporting, ISO/IEC 25010 quality attributes, OWASP WSTG categories for input/auth review

**Commands run**
- `npm test -- checkout`
- `npm run lint`
- `npx playwright test checkout.spec.ts --project=chromium`

**Summary**
- Passed: 12 checks
- Failed: 2 checks
- Not run / blocked: payment provider webhook sandbox unavailable

**Blockers**
1. Checkout API trusts client-provided discount amount.
2. Payment retry can create duplicate pending orders.

**Non-blocking risks**
1. Generated unit tests overuse render-only assertions.
2. Webhook delay behavior is not covered by automated tests.

**Recommendation**
No-go until the two blockers are fixed and covered by API/integration tests. After that, release can proceed with caveat that webhook sandbox validation remains a residual risk.
```
