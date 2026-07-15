# Bounded agent action readiness

## Use this when

Use this when assessing a small named set of agent actions without requesting a
repository-wide audit.

## Request template

```text
Adapt this request for {{repository}}.

Use $agent-readiness-audit to assess only whether an agent may {{bounded action
sequence}}. Inspect only {{named paths and controls}}. Stay read-only, use
bounded mode, and return the concise action matrix with evidence, approval
gates, skipped checks, and residual risk.
```

## Replace before running

- `{{repository}}`
- `{{bounded action sequence}}`
- `{{named paths and controls}}`
- `Approval owner: {{name or team}}`

## Required context

- Repository path: `{{absolute path}}`
- Action classes: `{{list}}`
- Named control surfaces: `{{paths}}`
- Approval owner: `{{name or team}}`
- Audit-only constraint: `true`

## What good looks like

- The report stays within the named paths and command budget.
- Each action receives a supported, conditional, blocked, or not-assessed
  verdict with evidence.
- No subagents or broad checks run in bounded mode.

## Illustrative handoff

This is an illustrative handoff, not evidence from a completed audit. It should
identify the action ceiling, missing gates, and one concrete next owner action.

## Verification checklist

- Confirm the command count and time budget.
- Confirm every skipped check is recorded.
- Confirm no files or external state changed.
- Confirm gated evidence lowers the action ceiling.

## Failure or escalation signals

- Missing named paths or action classes: return `NOT_ASSESSED`.
- Requested external write or production action: require the approval owner and
  do not execute it as part of the audit.
- A repository-wide scan is proposed: stop and remain in bounded mode.
