---
name: deep-bug-audit
description: Run deep bug hunts, broad audits, current-session, directory-targeted, multi-path, pull-request or session risk sweeps, production-readiness reviews, or text-instruction-driven bug searches across correctness, security, persistence, workflows, deployment, UI/API, observability, tests, and regression evidence.
---

# Deep Bug Audit

## Objective

Find real bugs, not style issues. Prefer confirmed, source-grounded findings
with a violated contract, reachable path, impact, verifier, missing test, and
mutation that would catch the regression. Measure audit efficiency at the end.

## Input routing

- If the user names one or more files or directories, audit only those targets
  plus their direct producers, consumers, tests, configs, and runtime surfaces.
- If the user provides only text instructions, infer the likely target surfaces
  from the text and repository search. Ask only when ambiguity would make the
  audit misleading or destructive.
- If no target is provided, audit the current session: current version-control
  state when available, recently touched files, visible task or handoff files,
  and adjacent tests and contracts. For Git repositories, inspect the current
  branch and `git diff/status`.
- Audit your own prior fixes in the same session. If the session already
  contains fixes you authored, treat the cumulative diff of those fixes as the
  primary audit envelope and state that explicitly. Fix-introduces-bug is a
  high-value target because authors are confirmation-biased toward their own
  changes being correct.
- If the request says "no fixes", "audit only", or "report only", do not patch
  production code. Creating a report artifact is allowed only when requested
  or clearly expected.
- Always honor repository instructions first, especially rules about external
  systems, generated files, live services, destructive operations, and broad
  test commands.

## Audit passes

1. Establish the audit envelope:
   - Record target paths, exclusions, branch, dirty state, user constraints,
     and whether the audit is current-session, path-targeted, multi-path, or
     text-driven.
   - Identify source-of-truth documents and local rules before source tracing.

2. Build a boundary map:
   - Entry points: HTTP, MCP, CLI, UI, workflow, job, event, runner, deploy,
     configuration, or test harness.
   - State transitions: queued, running, retry, recover, block, cancel, and
     done, including every terminal path.
   - Data contracts: request and response shapes, persistence rows, events,
     evidence references, generated artifacts, filesystem paths, branch or
     pull-request metadata, and external boundaries.
   - Producers and consumers: every field written by one component and
     consumed by another.
   - Single-source-of-truth constants: any sentinel, magic string, enum value,
     error code, or key duplicated as a literal in two or more components is a
     drift suspect. Trace the writer and reader through one shared definition
     where the architecture supports it.
   - Tests and verifiers: what proves each boundary and what only asserts
     helper behavior.

3. Sweep bug classes:

   **Run the repository's documented language static analyzer first, as a
   gate.** Use the narrowest command that covers the audit envelope and obey
   local restrictions on broad checks. Examples include Go `go vet`, Rust
   `cargo clippy`, TypeScript or JavaScript `tsc --noEmit` plus the project
   linter, Python `pylint` or `ruff`, and C or C++ `clang-tidy`. Treat every
   behavior-affecting finding as an audit signal that must be investigated
   before it can be dismissed or excluded. A clean analyzer run is a
   prerequisite, not a substitute, for the manual sweep below. If no
   applicable analyzer exists or it cannot run, record that check as `Not run`
   or `Gated` with the reason.

   - Contract drift: producer emits shape A while a consumer expects shape B.
   - State-machine gaps: missing terminal handling, retry loops, stale claims,
     duplicate work, partial success, cancellation, or out-of-order completion.
   - Persistence bugs: non-atomic writes, stale indexes, missing migration or
     backfill, wrong query scope, incorrect aggregate status, or pagination and
     cap mistakes.
   - Security and privacy: authorization gaps, path traversal, unsafe refs,
     secret or PII leakage, unbounded payloads, SSRF or injection, and unsafe
     generated artifacts.
   - Concurrency and reliability: lock scope, stale caches, non-idempotent
     retries, race-prone cleanup, resource leaks, and unbounded scans, fan-out,
     payloads, queues, temporary directories, workspaces, or artifacts.
   - Runtime and deployment: wrong service or binary, mismatched queues,
     branch or path policy bypass, generated-artifact drift, missing rebuild
     targets, or local-only proof of an external or operator-visible boundary.
   - Observability and operator behavior: misleading readiness, stale
     dashboards, missing categories, unsafe diagnostics, or no actionable next
     step.
   - UI and API behavior: type drift, nullable-field errors, stale optimistic
     state, hidden failed requests, and accessibility or interaction
     regressions.

4. Verify before reporting:
   - For each suspected bug, trace at least one reachable path from input to
     failure.
   - A fix that removes or relocates `defer`, `finally`, RAII, or another
     cleanup mechanism is a high-severity suspect until it is proven safe on
     panic, exception, cancellation, and early-return paths. A static analyzer
     may not catch cleanup that is called but no longer guaranteed to run.
   - Verify each acquired resource independently. When a function acquires more
     than one resource (file, lock, connection, handle, response body), check
     that the cleanup for each specific acquisition runs on every path; do not
     assume a cleanup pattern seen for one resource also covers another in the
     same body. Quote the exact line you rely on before asserting what it does.
     If no specific line supports a claim, do not make the claim.
   - Assume a reasonably current language runtime and standard library unless
     the code or its stated context says otherwise. Do not report a pattern as
     a bug solely because it was one in an older version that the current
     runtime resolves.
   - Prefer source evidence plus a focused test, command, fixture, runtime
     endpoint, log, or reproducible scenario.
   - Instruction text, helper-only assertions, and static inspection alone cannot
     claim runtime readiness when a real boundary is reachable and safe to
     exercise.
   - If evidence is incomplete, label the issue `Suspected` and separate it
     from confirmed findings. Do not inflate severity.
   - De-duplicate against known findings or prior handoffs. Mark known
     blockers but do not count them as new bugs unless the request asks for a
     rollup.

5. Assess tests adversarially:
   - Name the exact existing test that should have caught the bug and why it
     does not.
   - Name the missing regression test and the mutation it must kill.
   - If a path is manually verified only, explain why automated coverage is not
     feasible in scope.
   - If the repository has `test-coverage-audit`, use it for a dedicated
     missing or shallow test map. If it has `adversarial-test-review`, use it
     to prove tests catch regressions and to produce the fail-closed review
     verdict. Deep bug audit records the defect and required regression but
     does not replace those focused workflows.

## Finding status

Keep these statuses distinct in the report:

- `Confirmed`: source and reachable-path evidence support the finding.
- `Suspected`: plausible issue with incomplete evidence; do not count it as a
  confirmed finding.
- `Duplicate`: same issue already reported in the audit envelope or handoff.
- `Known`: pre-existing issue acknowledged by the repository or prior audit.
- `Gated`: required live, integration, credential, service, or operator
  prerequisite is unavailable.
- `Not run`: a relevant check was not attempted and has no current result.

Do not turn a missing runtime prerequisite into a clean result. Record the
exact gate, safe checks that did run, and the residual risk.

## Finding format

Use this shape for every confirmed finding:

```markdown
### N. Severity: short title

Contract violated:
- Expected invariant.

Evidence:
- `path:line` source, config, test, log, or endpoint evidence.

Reachable failure:
- How the system gets into the bad state.

Impact:
- User, operator, security, or data consequence.

Why tests missed it:
- Existing weak or missing coverage.

Required regression:
- Test name, boundary exercised, and mutation that must fail.

Fix boundary:
- Narrowest code area to change, or "not requested" for audit-only work.
```

If no confirmed or suspected bug exists in the audit scope, state that plainly
and briefly. Do not emit a finding-format block for a non-issue, and do not
manufacture a finding to have something to report.

Severity guide:

- `Critical`: exploitable security issue, data loss, destructive action,
  credential leak, or production-wide outage.
- `High`: reachable correctness or reliability bug that blocks delivery,
  corrupts state, leaks private operational data, or misleads operators.
- `Medium`: reachable bug with a bounded workaround or limited blast radius.
- `Low`: minor but real defect with low operational risk.

## Efficiency measurement

End every audit with:

- Time spent or estimated elapsed minutes.
- Paths and files reviewed.
- Commands, tests, and runtime checks run.
- Confirmed findings by severity.
- Suspected findings excluded from the score.
- Duplicate or known issues excluded from the score.
- Coverage gaps found.
- An efficiency summary from the bundled scorer when practical.

Locate `scripts/audit_efficiency_score.py` relative to this skill's installed
directory. Do not assume that the skill lives under a particular repository
directory. For example:

```bash
python3 /path/to/deep-bug-audit/scripts/audit_efficiency_score.py report.md --elapsed-minutes 90
python3 /path/to/deep-bug-audit/scripts/audit_efficiency_score.py audit.json --json
```

The scorer derives reviewed-file, command, and path counts from enumerated
evidence. Do not use self-reported scalar counts as proof of audit coverage.

When the target spans multiple components, persistence, workflows, security
boundaries, UI, or runtime services, load the bundled
`references/bug-taxonomy.md` from this skill directory and mark each relevant
category as covered, gated, not run, or not applicable.

## Usage examples

- [Current-session cross-boundary audit](references/examples/01-current-session-cross-boundary.md)
- [Targeted auth persistence audit](references/examples/02-targeted-auth-persistence-audit.md)
