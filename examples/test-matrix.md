# Example: Risk-Based Test Matrix

```markdown
| ID | Risk / Claim | Technique | Level | Check | Evidence | Result |
| --- | --- | --- | --- | --- | --- | --- |
| QA-001 | Checkout accepts valid cart and payment | ISTQB-UC | E2E | Happy path from cart to confirmation | `npx playwright test checkout.spec.ts` | Pass |
| QA-002 | Coupon length and format validation | ISTQB-EP / ISTQB-BVA | API | empty, valid, max length, max+1, unicode, expired | `npm test -- coupon` | Fail |
| QA-003 | Payment retry after decline | ISTQB-ST | Integration/E2E | failed payment -> retry -> success creates one order | targeted manual + planned E2E | Not run |
| QA-004 | Role boundary for admin-only discount codes | OWASP-WSTG-authz / ISO25010-security | API | normal user attempts admin coupon | `npm test -- authz` | Fail |
| QA-005 | Order creation survives payment webhook delay | ISO25010-reliability | Integration | delayed webhook does not lose paid order | not covered | Gap |
| QA-006 | Checkout remains usable on mobile | ISO25010-interaction | UI | 390px viewport, long product names, error state | Playwright screenshot | Pass |
| QA-007 | Generated tests catch real behavior | test-review / mutation-minded review | Unit | remove server validation and verify tests fail | static review | Gap |
```
