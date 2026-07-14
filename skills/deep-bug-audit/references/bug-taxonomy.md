# Deep Bug Audit Taxonomy

Use this checklist when a target spans more than one component, runtime
 boundary, or persistence or read-model contract. Mark a category not
 applicable only after checking the boundary map. Mark applicable checks as
 `GATED` when prerequisites are unavailable and `NOT RUN` when the check was
 not attempted. Do not invent a database, UI, deployment, or external-service
 boundary that the target does not have.

## Contract and shape drift

- Producer and consumer disagree on enum values, JSON tags, nullable fields,
  defaults, IDs, refs, path formats, branch names, queue names, or artifact
  names.
- A test asserts helper output but not the consumer-visible payload.
- A fallback path emits a different shape than the success path.
- A new field is written in memory but not persisted, indexed, serialized, or
  rendered.

## State machines and retries

- Terminal states skip cleanup, evidence, outbox, dashboard updates, or
  unlock or release actions.
- Retry attempts overwrite earlier chronology or lose failure-category details.
- Replacement runs reset counters that loop guards rely on.
- Soft failures become hard blocks after useful evidence exists.
- Cancellation, timeout, partial success, stale claims, duplicate claims, and
  out-of-order completion are untested.

## Persistence and aggregates

- Query scope is project-wide when the UI or API implies chain, run, user,
  branch, or task scope.
- Aggregate status is computed from any historical row rather than the latest
  relevant row.
- Status vocabularies differ between model, database, scripts, API, and
  frontend.
- Index write, delete, and backfill paths are asymmetric.
- Pagination, caps, or last-N queries hide the row that controls correctness.

## Security and data safety

- Path allowlists are checked after broader allow rules, or only at creation
  rather than execution.
- Deny lists use prefix matching without exact path-segment boundaries.
- Logs, traces, events, metrics, tests, or artifacts include raw prompts,
  source dumps, credentials, PII, provider payloads, or secret-shaped values.
- User-controlled refs reach filesystem, git, shell, URL, markdown, HTML, or
  SQL boundaries without validation.
- Recovery or admin paths skip the same authorization and path checks as
  primary paths.

## Concurrency and resource hygiene

- Cleanup ownership is split or only present in older workflows.
- A lock is held during store, network, filesystem, model, or process work.
- Cache invalidation is missing for create, update, status transition,
  delete, cancel, or retry.
- Background jobs are not idempotent across crashes, duplicate events, or
  replay.
- Resource usage is unbounded: scans, fan-out, payloads, workers, queues,
  temporary directories, workspaces, or artifacts.

## Runtime, deployment, and delivery

- Server and worker binaries are both needed but only one is rebuilt or tested.
- Worker queues differ between producer and consumer.
- One delivery path owns commit, push, or pull request changes while another
  path can publish or mutate branches outside that policy.
- Generated artifacts are verified but not declared for staging or commit.
- Live proof checks local files but not the external or operator-visible
  boundary.

## UI, dashboard, and observability

- Readiness or state is stale, global, or contradicted by the latest status.
- Operator-facing status hides the current stage, active task, failure
  category, or next action.
- Frontend types mirror an old backend shape after a semantic change.
- Long-lived streams lack timeout bypass, disconnect cleanup, or replay.
- Error categories are too generic to route recovery.

## Test-smell mutations

For each finding, pick at least one mutation that should fail:

- Delete the guard.
- Invert the branch.
- Drop the field from persistence or serialization.
- Replace latest-row logic with any-row logic.
- Remove one live status from an active or open set.
- Change a queue, path, or ref to a legacy value.
- Skip terminal cleanup.
- Treat no-diff or verifier failure as success.
- Allow a stale claim or duplicate completion.
- Remove safe diagnostic or category mapping.
