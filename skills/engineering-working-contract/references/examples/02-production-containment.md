# Contain a production issue before root cause is complete

## Use this when

Use this when an incident is active, the safe mitigation boundary is known, and
the complete root cause or permanent fix is not yet established.

## Request template

Adapt this request to the target repository and incident:

> Apply the engineering working contract to contain `{{incident symptom}}` in
> `{{service or workflow}}`. The observed impact is `{{bounded user or operator
> impact}}`. We know `{{safe fact}}`, but `{{unknown root-cause fact}}` remains
> unresolved.
>
> Inspect `{{logs, metrics, diff, runbook, or configuration}}`. Propose only
> the reversible mitigation `{{mitigation boundary}}`, explain what it does not
> prove, and do not implement a permanent fix without `{{approval owner}}` and
> `{{required evidence}}`. Report the containment result, the open root-cause
> work, and the next evidence gate.

## Replace before running

- `{{incident symptom}}`, `{{service or workflow}}`, and the impact with the
  current incident facts.
- `{{safe fact}}` and `{{unknown root-cause fact}}` with evidence-backed facts
  and explicit unknowns.
- `{{logs, metrics, diff, runbook, or configuration}}` with real sources.
- `{{mitigation boundary}}` with a reversible action that is authorized for the
  environment.
- `{{approval owner}}` and `{{required evidence}}` with the real gate.
- Add the rollback command and owner if the mitigation changes live state.

## Required context

Provide the incident timeline, affected scope, current evidence, safe rollback
or containment actions, permissions, alert ownership, deployment state, and the
definition of what containment means. State whether live changes are allowed.
Approval owner: {{incident commander or service owner}}.

## What good looks like

- The agent separates confirmed facts, hypotheses, mitigation, and permanent
  root-cause work.
- The proposed action is reversible, bounded, authorized, and tested against
  the stated failure mode.
- The handoff records what remains unknown and names the next evidence or
  approval gate without calling containment a complete fix.

## Illustrative handoff

This is an illustrative handoff shape, not an incident record:

```text
Status: {{CONTAINED, PARTIAL, or GATED}}
Confirmed facts: {{facts with source references}}
Mitigation: {{action and rollback owner}}
Not proven: {{root cause or permanent-fix evidence still missing}}
Next gate: {{evidence, approval, or live check required}}
```

## Verification checklist

- Confirm the mitigation's scope, authorization, reversibility, and rollback
  path before applying it.
- Capture the before and after signals that define containment.
- Check that the mitigation does not hide data loss, retry amplification, or a
  second failure mode.
- Record the permanent root-cause investigation as open work with an owner.

## Failure or escalation signals

Stop before changing live state when authorization, rollback, or impact scope
is missing. Return `PARTIAL` when containment evidence exists but the root cause
is unresolved. Escalate when the mitigation could delete data, alter customer
state, suppress evidence, or expand the incident's blast radius.
