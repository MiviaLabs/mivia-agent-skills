# Fix a concurrency invariant

## Use this when

Use this when a scheduler, worker, queue, or shared-state change can race and
the request needs the standing engineering contract before implementation.

## Request template

Adapt this request to the target repository:

> Apply the engineering working contract to fix the concurrency issue in
> `{{implementation path or symbol}}`. The suspected invariant is
> `{{state that must remain true}}`, and the reachable failure is
> `{{duplicate, lost, stale, or out-of-order behavior}}`.
>
> Inspect `{{relevant tests, configuration, and runtime evidence}}` first.
> Make the smallest complete change. Run `{{focused concurrency test}}` before
> `{{additional race, package, or integration check}}`, if that check exists.
> Do not claim concurrency safety beyond the checks you execute. Report the
> changed invariant, evidence, residual risk, and required approval.

## Replace before running

- `{{implementation path or symbol}}` with a real source path and symbol.
- `{{state that must remain true}}` with the repository's invariant.
- `{{duplicate, lost, stale, or out-of-order behavior}}` with a reachable
  failure mode.
- `{{relevant tests, configuration, and runtime evidence}}` with existing
  paths, commands, logs, or fixtures.
- `{{focused concurrency test}}` and the optional additional check with real
  commands available in the target repository.
- Add `{{approval owner}}` when the change affects production coordination or
  deployment behavior.

## Required context

Provide the current diff, the competing actors, shared state, cancellation and
retry behavior, the invariant, available race or stress checks, and the
definition of done. Include any repository rule that limits broad test runs.

## What good looks like

- The agent names the invariant and traces one reachable failure path before
  editing.
- The patch is scoped to the smallest complete ownership boundary and includes
  a regression check for the race.
- The handoff separates executed evidence, unverified concurrency risk, and
  approval needed for consequential changes.

## Illustrative handoff

This is an illustrative handoff shape, not evidence from an executed task:

```text
Status: {{PASS or PARTIAL for the executed scope}}
Invariant: {{one sentence}}
Changed: {{files or symbols actually changed}}
Checks: {{commands actually run and their results}}
Remaining risk: {{race, stress, runtime, or deployment evidence not obtained}}
Approval: {{owner and decision still required, or None}}
```

## Verification checklist

- Confirm the focused regression test fails against the old behavior and passes
  against the change.
- Run the narrowest available race, stress, or deterministic interleaving
  check.
- Review cancellation, retry, duplicate, and out-of-order paths when they are
  part of the changed boundary.
- Compare the final diff with the invariant and record checks that were not run.

## Failure or escalation signals

Return `PARTIAL` when the regression check passes but race-enabled, integration,
or runtime evidence is unavailable. Stop and request approval when the fix
changes production coordination, data ownership, or a deployment contract.
Mark a suspected race as unresolved when the path is plausible but not
reproduced or covered by a focused test.
