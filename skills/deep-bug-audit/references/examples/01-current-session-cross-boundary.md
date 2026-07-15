# Audit a current diff across system boundaries

## Use this when

Use this when the current session changes multiple connected boundaries such as
an API, persistence query, retry path, and dashboard state, and the request is
an audit rather than an automatic fix.

## Request template

Adapt this request to the current repository:

> Audit the current diff across `{{API path}}`, `{{persistence path}}`,
> `{{retry or workflow path}}`, and `{{dashboard or consumer path}}` before
> merge. Do not fix production code unless separately approved.
>
> Establish the audit envelope, trace one reachable path for each suspected
> failure, run `{{documented analyzer}}`, and inspect `{{focused tests and
> runtime checks}}`. For each finding, report status, impact, source evidence,
> missed regression, and a mutation that should fail. Include efficiency and
> all checks actually run.

## Replace before running

- Replace every path placeholder with the current diff and direct boundary
  consumers.
- Replace `{{documented analyzer}}`, focused tests, and runtime checks with
  commands supported by the repository.
- State the branch, dirty state, exclusions, and whether no-fix scope applies.
- Add any live environment or credential gate instead of implying it is
  available.

## Required context

Provide the current diff, repository instructions, API and persistence
contracts, state transitions, retry and cancellation behavior, dashboard
consumer expectations, test commands, analyzer command, and runtime access.
Approval owner: {{reviewer or release owner}}.

## What good looks like

- The audit maps producers, consumers, state transitions, and a reachable
  failure rather than listing style concerns.
- Findings distinguish `Confirmed`, `Suspected`, `Known`, `Gated`, and `Not run`
  using source-grounded evidence.
- Each confirmed finding includes a missing regression and mutation target, with
  no-fix scope and efficiency reported honestly.

## Illustrative handoff

This is an illustrative handoff shape, not audit evidence:

```text
Audit envelope: {{branch, diff, target paths, exclusions}}
Finding: {{status and severity}} - {{short title}}
Reachable failure: {{input to impact path}}
Evidence: {{source, test, log, or endpoint references}}
Regression: {{test and mutation that should fail}}
Checks: {{commands actually run}}
Gates: {{live or external evidence unavailable}}
```

## Verification checklist

- Inspect the diff and direct producers, consumers, tests, and configuration.
- Run the documented static analyzer before the manual sweep.
- Trace API, persistence, retry, and dashboard behavior through one reachable
  path when the boundary is in scope.
- Test or name missing coverage for stale state, malformed input, authorization,
  retries, and terminal artifacts when applicable.
- Confirm the report does not silently patch production code.

## Failure or escalation signals

Mark evidence `Gated` or `Not run` when runtime, credentials, or services are
unavailable. Mark a plausible but unproven issue `Suspected`. Stop and request
scope clarification when the current diff or direct consumers cannot establish
the audit envelope.
