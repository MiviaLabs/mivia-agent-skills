# Audit named authorization and persistence paths

## Use this when

Use this when a reviewer names authorization and query paths and requires a
source-grounded audit with an explicit no-fix constraint.

## Request template

Adapt this request to the target repository:

> Audit only `{{authorization entry point}}` and `{{persistence query path}}`,
> plus their direct callers, consumers, tests, and configuration. Do not modify
> production code. Check tenant, identity, scope, query filtering, error
> propagation, and persistence ownership for `{{resource or data contract}}`.
>
> Run `{{narrow analyzer}}` and `{{focused authorization or query tests}}`.
> Report only source-grounded findings. Classify uncertainty explicitly and
> name the smallest regression test and mutation needed for each gap.

## Replace before running

- Replace both path placeholders and the resource contract with real targets.
- Define the allowed direct-boundary expansion and exclusions.
- Replace analyzer and focused-test placeholders with available commands.
- State the tenant, role, identity, and data-scope assumptions.
- Add live auth or database checks as `Gated` if they cannot run.

## Required context

Provide the authorization model, caller identity, tenant or project scope,
query parameters, repository rules, migrations or indexes that affect the path,
focused tests, static analyzer, and the explicit no-fix instruction.
Approval owner: {{security or service owner}}.

## What good looks like

- The audit stays within named paths and direct boundaries while checking
  authorization and query scope together.
- Findings cite the source and reachable failure, and separate confirmed issues
  from plausible but unverified concerns.
- The handoff includes no production edits and names precise negative tests and
  mutations for missing coverage.

## Illustrative handoff

This is an illustrative handoff shape, not an authorization finding:

```text
Scope: {{named paths and direct boundaries}}
Status: {{Confirmed, Suspected, Gated, or Not run}}
Contract: {{authorization or query invariant}}
Evidence: {{source and test references}}
Impact: {{resource or tenant consequence}}
Missing regression: {{test input, expected denial or isolation, mutation}}
Production changes: none
```

## Verification checklist

- Check unauthenticated, wrong-tenant, wrong-role, missing-scope, and valid
  access paths when they apply.
- Trace query filters and resource ownership from the authorization decision to
  persistence.
- Check normalization, empty scope, duplicate identity, and error paths.
- Run the narrow analyzer and focused tests, then record live database or auth
  evidence that was not available.
- Confirm the working tree contains no production fix from the audit.

## Failure or escalation signals

Mark a missing live database or identity check `Gated`, not clean. Mark an
unproven privilege or isolation concern `Suspected`. Stop when the requested
scope is too broad to audit without changing the no-fix or direct-boundary
constraint.
