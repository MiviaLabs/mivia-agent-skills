# Agent runtime readiness with unavailable enforcement

## Use this when

Use this when repository instructions and CI configuration are visible, but
runtime hooks, permission boundaries, or protected-branch settings cannot be
exercised from the current environment.

## Request template

```text
Adapt this request for {{repository}} and action class {{external writes or deploys}}.

Use $agent-readiness-audit-go in read-only mode. Inspect the documented controls,
then record every unavailable runtime, credential, service, or operator gate as
GATED or NOT_RUN. Do not install tools, access production, or invent results.
Use the strict report template and fail closed.
```

## Replace before running

- `<repository>`
- `<action class>`
- `<missing service or permission>`
- `Approval owner: <name or team>`

## Required context

- Repository path: `<absolute path>`
- Revision: `<commit or branch>`
- Action class: `<external write, deploy, or destructive action>`
- Missing prerequisite: `<service, permission, credential, or owner evidence>`
- Approval owner: `<name or team>`
- Audit-only constraint: `true`

## What good looks like

- Documentation is reported as documented-only rather than enforced.
- The scoped verdict is conditional, blocked, or not assessed.
- The report names the exact owner and evidence needed to advance the gate.

## Illustrative handoff

This is an illustrative handoff, not evidence from a completed audit. It should
identify the missing gate, the action it protects, and the exact verification
needed before autonomy can increase.

## Verification checklist

- Confirm unavailable controls are present in the command and evidence log.
- Confirm no skipped or gated check is presented as passing.
- Confirm the maximum granted level does not exceed the supported level.
- Confirm prohibited actions and required approvals are explicit.

## Failure or escalation signals

- Any request to use production credentials or mutate external state: stop and
  escalate to the approval owner.
- Any missing control-plane target: return `NOT_ASSESSED` rather than expanding
  into application correctness or production-readiness review.
- Any contradiction between documentation and executable behavior: create a
  finding and lower the autonomy decision.
