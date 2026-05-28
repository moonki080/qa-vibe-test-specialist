# Example: Defect Report

```markdown
## Title
Checkout API trusts client-provided discount amount

## Environment
- Branch: `feature/checkout`
- Surface: `POST /api/checkout`
- Test data: cart total 42, forged `discountAmount: 9999`

## Preconditions
- User is authenticated as a normal customer.
- Cart contains at least one item.

## Steps To Reproduce
1. Open browser dev tools or use an API client.
2. Send a checkout request with a valid cart and `discountAmount: 9999`.
3. Observe the created order total.

## Expected Result
Server recalculates discount from trusted coupon and cart data. Client-provided discount amount is ignored.

## Actual Result
Server accepts the request body discount and creates an order with an invalid total.

## Evidence
- Static review: `route.ts` reads `discountAmount` from request JSON.
- Missing test: no API negative case for forged pricing fields.

## Severity
High

## Priority
P1

## Alignment
`ISO25010-security`, `OWASP-WSTG-input`, `ISTQB-EP`, `CSTS-dynamic-test`

## Suggested Next Action
Move discount calculation server-side, reject unexpected pricing fields, and add API tests for forged discount, expired coupon, and role-restricted coupon.
```
