# Standards Map

Use this file to explain why a test approach is credible without claiming formal certification.

## Source Roles

- CSTS: Use as a Korean professional testing-practice anchor for terminology, test design discipline, defect reporting, static/dynamic testing, and test management expectations. Cite TTA as the CSTS operator when source attribution is needed.
- ISTQB CTFL/Advanced: Use for globally recognized testing terminology, test process thinking, black-box, white-box, experience-based, and collaboration-based techniques, test management, defect reporting, and test automation risk framing.
- ISO/IEC/IEEE 29119: Use for test process, test documentation, and test design traceability. Part 1 covers concepts, Part 2 processes, Part 3 documentation, and Part 4 design techniques.
- ISO/IEC 25010: Use for product quality attribute coverage. For current 2023 framing, consider attributes such as functional suitability, performance efficiency, compatibility, interaction capability, reliability, security, maintainability, flexibility, and safety when relevant. For formal audit work, verify the current official standard text.
- OWASP WSTG: Use for web application and web-service security testing scope. Prefer versioned WSTG identifiers in reports when precise traceability matters.

## Practical Traceability Tags

Use compact tags in test plans and findings:

- `CSTS-static-review`: requirements, design, code, or test artifact review.
- `CSTS-dynamic-test`: executable behavioral verification.
- `ISTQB-EP`: equivalence partitioning.
- `ISTQB-BVA`: boundary value analysis.
- `ISTQB-DT`: decision table testing.
- `ISTQB-ST`: state transition testing.
- `ISTQB-UC`: use-case or scenario testing.
- `ISTQB-WB`: white-box branch, condition, path, or data-flow review.
- `ISTQB-EXP`: exploratory, checklist-based, or error-guessing testing.
- `ISO29119-plan`: test planning, scope, risks, entry/exit criteria.
- `ISO29119-design`: test condition, test case, test procedure, and traceability design.
- `ISO29119-report`: test execution, incident, completion, or summary reporting.
- `ISO25010-functional`: functional correctness, completeness, or appropriateness.
- `ISO25010-performance`: latency, throughput, resource use, or capacity.
- `ISO25010-compatibility`: interoperability, coexistence, browser/device/API compatibility.
- `ISO25010-interaction`: usability, accessibility, learnability, operability, user error protection.
- `ISO25010-reliability`: fault tolerance, recoverability, availability, consistency.
- `ISO25010-security`: confidentiality, integrity, authentication, authorization, accountability.
- `ISO25010-maintainability`: modularity, analyzability, testability, modifiability.
- `OWASP-WSTG-authn`: authentication testing.
- `OWASP-WSTG-authz`: authorization testing.
- `OWASP-WSTG-input`: input validation and injection-oriented checks.
- `OWASP-WSTG-session`: session management checks.
- `OWASP-WSTG-config`: configuration and deployment review.

## Reporting Language

Use careful language:

- Good: "This plan is aligned with CSTS/ISTQB concepts and ISO/IEC/IEEE 29119-style test design."
- Good: "OWASP WSTG categories were used to scope non-destructive security review."
- Avoid: "Certified by CSTS", "ISO 29119 compliant", or "OWASP approved" unless a real formal assessment exists.

## Official Source Pointers

When links are needed, prefer:

- TTA Academy CSTS qualification introduction.
- ISTQB official CTFL syllabus and glossary pages.
- ISO pages for ISO/IEC/IEEE 29119 and ISO/IEC 25010.
- OWASP WSTG project page and versioned scenario pages.
