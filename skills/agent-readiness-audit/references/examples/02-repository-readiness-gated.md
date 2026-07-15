# Repository readiness with gated enforcement

## Use this when

Use this when the user explicitly requests a repository-wide control-plane audit
but protected CI, permissions, or runtime evidence is unavailable.

## Request template

```text
Adapt this request for {{repository}} at {{revision}}.

Use $agent-readiness-audit for a repository-wide audit of {{action classes}}.
Use no more than two disjoint control-plane workstreams. Do not modify files,
install tools, access production, or invent results. Mark unavailable checks as
GATED or NOT_RUN and complete the strict report template.
```

## Replace before running

- `{{repository}}`
- `{{revision}}`
- `{{action classes}}`
- `{{missing service, permission, or owner evidence}}`
- `Approval owner: {{name or team}}`

## Required context

- Repository path: `{{absolute path}}`
- Revision: `{{commit or branch}}`
- Action classes: `{{list}}`
- Missing prerequisite: `{{description}}`
- Approval owner: `{{name or team}}`

## What good looks like

- Documentation-only controls are not reported as enforced.
- Missing runtime or permission evidence produces a gated or conditional
  result.
- The report names the exact owner and verifier needed to advance the gate.

## Illustrative handoff

This is an illustrative handoff, not evidence from a completed audit. It should
identify the blocking gate, protected action, and required verification.

## Verification checklist

- Confirm the immutable baseline and audit-only state.
- Confirm all workstreams have explicit scope and evidence IDs.
- Confirm no gated or not-run check is presented as passing.
- Confirm the granted autonomy level does not exceed the supported level.

## Failure or escalation signals

- Production credentials or external writes requested: stop and escalate.
- A subagent widens scope or edits files: discard its result and record the
  coordination failure.
- No bounded control surface can be found: return `NOT_ASSESSED`.
