# Agent Readiness Audit Workstream Contract

Use no more than two workstreams against one immutable repository snapshot.
Each agent returns evidence only and must not modify files, install tools,
access production systems, widen scope, or duplicate another workstream's
ownership.

For repository-wide mode, use the user-provided deadline or a default
30-minute deadline. The coordinator may poll less frequently and must not mark
a workstream failed merely because it has not returned within 60 or 90 seconds.
Declare a workstream stalled only after the deadline, an explicit error, or
repeated evidence of no progress.

## Workstream ownership

| ID | Owner | Scope | Output |
| --- | --- | --- | --- |
| WS1 | Instructions and executable enforcement | Agent instructions, hooks, command wrappers, policy files, permissions, protected actions, and bypass paths | Control inventory and enforcement findings |
| WS2 | CI, evaluations, packaging, and runtime wiring | CI checks, branch rules, skill metadata and evaluations, installation, packaging, and safe runtime probes | Guardrail matrix and evidence gaps |

## Required subagent output

Each workstream must return:

```text
Workstream: WS<n>
Scope: exact paths, packages, workflows, and tools inspected
Excluded scope: paths and reasons
Evidence IDs: E-### sequence owned by this workstream
Findings: AR-### candidates, or None identified
Commands: executed and not-run entries
Unknowns: missing evidence and required verifier
Handoff: highest-risk conclusion and next action
```

Each finding candidate must include its classification, severity, exact scope,
evidence location, reachable agent failure scenario, current protection,
bypass path, recommendation, preferred enforcement mechanism, and autonomy
impact. Unsupported claims must be marked `LIKELY_RISK` or discarded.

## Coordinator rules

- Deduplicate by root cause, not by workstream.
- Prefer executable evidence over documentation and direct evidence over
  inference.
- Require corroboration for Critical and High findings, or label the finding
  `single-source evidence`.
- Do not resolve conflicts by majority vote.
- Preserve unresolved conflicts as `MISSING_EVIDENCE` and lower the autonomy
  recommendation.
- Do not claim all areas were audited unless the coverage ledger proves it.
- Do not expand into application correctness, general security, supply chain,
  deployment, or production readiness unless a named agent control directly
  requires that boundary.
