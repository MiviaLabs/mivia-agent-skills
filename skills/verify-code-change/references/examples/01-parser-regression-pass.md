# Verify a parser regression fix

## Use this when

Use this when a parser or decoder change has a focused regression test and the
request is to determine whether the executed verification scope is ready for
review.

## Request template

Adapt this request to the target repository:

> Verify the parser fix in `{{parser path or symbol}}` for
> `{{malformed or boundary input}}`. Inspect the diff and the regression test
> at `{{test path or symbol}}`.
>
> Run `{{focused test command}}` first. Then run the justified checks
> `{{lint, package, or integration command}}` if they are available. Report
> `PASS` only for checks actually executed successfully. Include skipped checks,
> parser input coverage, and residual risk.

## Replace before running

- `{{parser path or symbol}}` and `{{test path or symbol}}` with real paths.
- `{{malformed or boundary input}}` with the exact regression class without
  embedding secrets or customer data.
- `{{focused test command}}` with a command that runs the regression.
- `{{lint, package, or integration command}}` with available commands, or say
  that the check is unavailable.
- Add the required review owner and branch or package gate if applicable.

## Required context

Provide the current diff, parser contract, accepted and rejected input forms,
fixture scope, focused test command, available static or package checks, and any
downstream consumer that depends on the parsed shape.
Approval owner: {{code owner or reviewer}}.

## What good looks like

- The focused regression test runs first and asserts the changed parser
  behavior, including the closest valid input when relevant.
- Additional checks are justified by the changed boundary and are not reported
  as executed when unavailable.
- The result status is limited to the executed scope and the handoff names
  remaining parser or integration uncertainty.

## Illustrative handoff

This is an illustrative handoff shape, not a test result:

```text
Verification result: {{PASS, PARTIAL, or FAIL}}
Scope: {{parser behavior and files reviewed}}
Checks executed: {{commands and observed results}}
Checks skipped: {{commands not available or not run}}
Remaining risk: {{unverified input, consumer, or packaging path}}
```

## Verification checklist

- Run the focused regression and its closest valid positive case.
- Check malformed, empty, boundary, and encoding-sensitive inputs when they are
  part of the parser contract.
- Run only the justified lint, package, or integration checks that exist.
- Review the diff for broad normalization, swallowed errors, or fixture changes
  that weaken the regression.

## Failure or escalation signals

Return `FAIL` when the focused regression fails or the diff violates the parser
contract. Return `PARTIAL` when useful checks pass but a required downstream or
integration boundary is unavailable. Do not convert an unrun check into `PASS`.
