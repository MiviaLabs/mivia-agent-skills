# Verification Is Part of Delivery

Generated code is not delivered code.

## Principle

An engineering task should not be declared complete until the required behavior has been verified to a level appropriate for its risk and the remaining uncertainty has been disclosed.

When required verification is unavailable, the correct result is partial or blocked, not complete.

## Required behavior

- Reproduce the failure or establish the expected behavior when feasible.
- Run the smallest relevant check first.
- Expand verification according to blast radius and risk.
- Add regression coverage for meaningful behavior changes when feasible.
- Review the final diff for unrelated changes and unnecessary complexity.
- Report anything that could not be verified.
- Keep completion claims limited to the executed scope.

## Verification ladder

1. Focused reproduction or unit test
2. Relevant lint, type-check, or static analysis
3. Package or service test suite
4. Build or integration test
5. Broader validation for high-risk changes
6. Independent review when the impact justifies it

The ladder is guidance, not ceremony. Select checks that cover the real failure modes.

## Failure pattern

Agents often stop after producing a plausible patch. That moves uncertainty downstream to reviewers, CI, staging, or production.

## Boundary

Verification reduces uncertainty. It does not prove the absence of defects. A one-line local change does not need the same process as a security-sensitive migration. The requirement is evidence appropriate to the risk.
