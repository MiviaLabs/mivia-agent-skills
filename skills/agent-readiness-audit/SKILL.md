---
name: agent-readiness-audit
description: Audit repository control-plane protections governing named coding-agent actions, including instructions, hooks, command wrappers, CI, policy, permissions, evaluations, packaging, and external-effect gates. Use when the user asks whether an agent may safely perform named actions or whether agent guardrails are enforced. Do not use for application bug hunts, ordinary change verification, general security audits, or production readiness.
---

# Agent Readiness Audit

## Objective

Determine which controls governing named coding-agent actions are enforced,
documented-only, partial, gated, not run, or contradicted. Assess the highest
action level supported by evidence. Do not infer effectiveness from tool
presence, documentation, coverage, or passing tests alone.

This skill audits the repository control plane. It does not certify application
correctness, general security, supply chain, production readiness, or release
readiness. Route source-grounded bug hunts to `bug-audit` and implemented
change verification to `verify-code-change`.

## First decision

Decide the mode before reading bundled references or launching tools. If the
user names a small action sequence and does not explicitly request a
repository-wide audit, enter bounded mode immediately. In bounded mode, do not
read the full report template, workstream contract, or broad command guidance;
use only the bounded rules and output below. Never launch subagents in bounded
mode.

## Activation boundary

Activate only for questions about coding-agent guardrails, permissions, safe
commands, autonomy limits, delegated-agent readiness, or enforcement of agent
instructions.

Do not activate for ordinary implementation, debugging, post-change
verification, application bug hunts, general security reviews, deployment
readiness, or release readiness without an agent-action question.

## Scope and modes

Inspect only the control-plane surfaces relevant to the named action classes:

- agent instructions and precedence;
- hooks, command wrappers, policy files, permissions, and CI;
- skill metadata, activation evaluations, packaging, and installation;
- tests or runtime probes that enforce those controls;
- application code only when it implements a named control or is the minimum
  boundary needed to verify it.

If no action class or bounded control surface is identifiable, return
`NOT_ASSESSED` instead of widening scope.

### Bounded action-set mode

Use bounded mode when the user names a small action sequence but does not ask
for a repository-wide audit. Bounded mode assesses readiness only. It does not
edit files, commit, push, open pull requests, or call external write tools.

In bounded mode:

- inspect only named paths and controls;
- do not run workstreams, subagents, broad scans, broad tests, full builds,
  generators, migrations, or dependency resolution;
- use a hard limit of six shell commands and five minutes total, including
  retries, with a 60-second timeout per command;
- mark unnamed paths and focused tests `NOT_RUN` rather than discovering wider
  scope;
- stop when each named action has evidence or a blocker.

Bounded mode has a default five-minute audit budget because it is intended for
a small action set. A user-provided lower or higher budget overrides it.

Return only the bounded output contract:

```text
Scope: <named paths and action classes>; budget: <used>/<limit>

| Action | Verdict | Evidence or blocker |
| --- | --- | --- |
| <action> | <SUPPORTED_WITHIN_SCOPE / CONDITIONAL / BLOCKED / NOT_ASSESSED> | <one sentence> |

Commands: <executed>; skipped: <broad commands not run>
Approval gate: <one sentence>
Residual risk: <one sentence>
```

Do not emit the full template, workstream reports, raw logs, or repository-wide
findings in bounded mode.

### Repository-wide mode

Use repository-wide mode only when explicitly requested and when the declared
budget supports it. Unless the user specifies otherwise, use a 30-minute audit
budget for repository-wide mode, including subagent work. Allow a delegated
workstream up to that budget before declaring it stalled; a 60- or 90-second
polling timeout is not a failure criterion for this mode. Read
[workstream-contract.md](references/workstream-contract.md)
and use no more than two disjoint control-plane workstreams when parallel
review is justified. Never delegate broad application correctness, general
security, supply chain, or production audits.

Read [command-safety.md](references/command-safety.md) before running
repository-controlled commands. Use the narrowest safe command and record
executed and skipped checks.

## Required operating rules

- Record repository, immutable commit, branch, worktree state, tools, services,
  action classes, scope, budget, and environment limitations.
- Do not modify source, tests, generated files, dependencies, databases,
  external systems, branches, or CI settings.
- Treat tests, hooks, generators, scripts, builds, and dependency resolution as
  executable code.
- Use deny-by-default assumptions for network, credentials, filesystem scope,
  and deployment access. Do not expose secrets.
- In bounded mode, action, path, command, time, and output limits are hard
  boundaries and override the repository-wide procedure and full report.
- Never call a check passing unless it executed successfully.

## Evidence semantics

Classify every capability as:

- `ENFORCED`: source evidence plus an executed test, hook, CI check, or runtime
  probe demonstrates the control;
- `DOCUMENTED_ONLY`: instructions describe it but enforcement was not shown;
- `PARTIAL`: some boundary evidence exists but a required boundary is missing;
- `GATED`: required runtime, credential, service, or operator evidence is
  unavailable;
- `NOT_RUN`: a relevant check was not attempted;
- `CONTRADICTED`: documentation and executable behavior disagree.

Missing evidence lowers the supported ceiling. It never becomes a clean result.
Critical and High findings require corroboration or an explicit
`single-source evidence` label.

## Autonomy levels

- Level 0: observe, inspect, and report only.
- Level 1: read-only analysis and safe local checks.
- Level 2: bounded local edits and focused tests.
- Level 3: commit or draft pull request after required checks.
- Level 4: push, merge, release, or deploy after protected review and live proof.
- Level 5: destructive or production-changing actions with per-action approval
  and rollback controls.

Always require human approval for authentication, authorization, secrets, CI or
workflow changes, policy files, dependencies, migrations, production
configuration, persistence semantics, tenant isolation, command execution, and
network-facing behavior unless protected evidence establishes a safer rule.

Cap autonomy when required evidence is unresolved, unknown, bypassable,
skipped, flaky, suppressed, timed out, or conditional.

## Repository-wide output

For repository-wide mode only, complete
[audit-report-template.md](references/audit-report-template.md). Keep every
required heading and use evidence IDs `E-001`, findings `AR-001`, and explicit
`NOT_RUN`, `GATED`, or `None identified` entries. Do not invent results.

## Usage examples

- `references/examples/01-bounded-action-readiness.md`
- `references/examples/02-repository-readiness-gated.md`

## Failure handling

- Missing command, service, permission, or runtime evidence: return `GATED` or
  `NOT_RUN`.
- Missing target or action class: return `NOT_ASSESSED`.
- Unsupported subagent claim: discard it or mark `LIKELY_RISK`.
- Do not convert blocked verification into a positive autonomy result.
