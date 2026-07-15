# Verify a database migration with a missing deployment gate

## Use this when

Use this when a migration changes persisted data or schema and local syntax or
focused checks are available, but deployment-critical integration evidence is
not available in the current environment.

## Request template

Adapt this request to the target repository:

> Verify the migration in `{{migration path or revision}}` for
> `{{table, index, or data contract}}`. Inspect the migration, rollback policy,
> application compatibility, and `{{available focused check}}`.
>
> Run `{{safe local command}}` and any available compatibility or schema check.
> The `{{missing integration or deployment check}}` is unavailable because
> `{{specific gate}}`. Report `PARTIAL` unless every required deployment check
> actually runs. Identify the approval owner and next gate before release.

## Replace before running

- `{{migration path or revision}}`, data contract, and rollback policy with
  repository-specific details.
- `{{available focused check}}` and `{{safe local command}}` with real commands.
- `{{missing integration or deployment check}}` and `{{specific gate}}` with
  the exact unavailable evidence and reason.
- Add the compatibility window, backup or rollback owner, and release approval
  gate when applicable.

## Required context

Provide the migration and application versions, schema and data impact, forward
and rollback behavior, deploy order, compatibility requirements, available
database fixtures, credentials or environment limits, and release criteria.
Approval owner: {{database or release owner}}.

## What good looks like

- The migration is treated as a persistence and deployment boundary, not only a
  syntax check.
- Safe local evidence is collected while unavailable integration evidence is
  named precisely and never implied to have run.
- The handoff returns `PARTIAL`, states the release gate, and identifies the
  owner of the next verification.

## Illustrative handoff

This is an illustrative handoff shape, not deployment evidence:

```text
Verification result: PARTIAL
Checks executed: {{safe local checks and results}}
Not run: {{integration, rollback, or deployment check and exact reason}}
Compatibility risk: {{reader/writer or rollout concern}}
Release gate: {{required owner, environment, and evidence}}
```

## Verification checklist

- Inspect forward and rollback SQL or equivalent migration behavior.
- Check old and new application versions against the changed schema when the
  deployment is rolling or mixed-version.
- Run the narrowest available schema, fixture, or static check.
- Confirm the unavailable integration or deployment check is recorded as a
  gate, not as a successful result.

## Failure or escalation signals

Return `PARTIAL` when deployment-critical evidence is unavailable. Stop before
release when rollback, backup, compatibility, data-loss impact, or approval
ownership is unclear. Return `FAIL` when the migration or available check
violates the stated contract.
