# Repository autonomy readiness audit

## Use this when

Use this when deciding whether an agent may inspect, edit, test, commit, or open
a pull request in a repository with multiple control surfaces.

## Request template

```text
Adapt this request for {{repository}} at {{commit}}.

Use $agent-readiness-audit-go to assess these named action classes:
{{read-only inspection, bounded local edits, test execution, commits, draft PRs}}

Audit only the repository control plane. Use subagents for disjoint workstreams
when available. Do not modify files or external state.
Use the strict report template and return evidence IDs, command records,
blocking gates, permitted actions, prohibited actions, and residual risk.
```

## Replace before running

- `<repository>`
- `<commit>`
- `<action classes>`
- `Approval owner: <name or team>`

## Required context

- Repository path: `<absolute path>`
- Revision: `<commit or branch>`
- Action classes in scope: `<list>`
- Approval owner: `<name or team>`
- Available services and credentials: `<none or explicit safe test services>`
- Do not grant production or credentialed network access for this audit.

## What good looks like

- The report distinguishes enforced controls from documentation-only claims.
- Every supported action has evidence, a verifier, and a fail-closed gate.
- Unknown CI, permission, or runtime evidence lowers the autonomy ceiling.

## Illustrative handoff

This is an illustrative handoff, not evidence from a completed audit. It should
state whether the named actions are supported within scope, which gates remain
unknown, and the next owner action.

## Verification checklist

- Confirm the immutable revision and clean audit-only state.
- Confirm every command has an execution or not-run record.
- Confirm the report uses the required template and evidence IDs.
- Confirm no unqualified safe, ready, or maximum-autonomy claim appears.

## Failure or escalation signals

- Missing branch protection or permission evidence: mark the result gated.
- Tests or hooks require unavailable services: record the limitation and cap
  autonomy.
- A subagent widens scope or modifies files: discard its unsupported result and
  report the coordination failure.
