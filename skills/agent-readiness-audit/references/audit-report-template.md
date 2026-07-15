# Agent Readiness Audit Report

Use this file as the report skeleton. Keep every required heading. Replace
angle-bracket placeholders, add evidence, and write `None identified`, `Not
applicable`, `Not run`, or `Gated` where appropriate. Do not invent results.

<!-- AGENT_READINESS_AUDIT:START -->
```json
{
  "schema_version": "1",
  "audit_id": "<required unique id>",
  "repository": "<name>",
  "revision": "<commit or working-tree identifier>",
  "audit_only": true,
  "action_classes": [],
  "scoped_verdict": "SUPPORTED_WITHIN_SCOPE|CONDITIONAL|BLOCKED|NOT_ASSESSED",
  "autonomy_decision": "BLOCKED|RESTRICTED|CONDITIONALLY_ALLOWED|ALLOWED",
  "maximum_supported_level": "0|1|2|3|4|5",
  "maximum_granted_level": "0|1|2|3|4|5",
  "blocking_gate_ids": [],
  "unknown_gate_ids": [],
  "unreviewed_paths": [],
  "evidence_ids": [],
  "finding_ids": [],
  "gate_ids": []
}
```
<!-- AGENT_READINESS_AUDIT:END -->

## 0. Audit baseline and scope [REQUIRED]

| Field | Value |
| --- | --- |
| Repository | `<path and name>` |
| Commit | `<full SHA>` |
| Branch | `<branch>` |
| Worktree state | `<clean or exact status>` |
| Audit mode | `repository-wide / bounded / current snapshot` |
| Time and command budget | `<value>` |
| Scope included | `<paths and surfaces>` |
| Scope excluded | `<paths and reason>` |
| Go and tool versions | `<versions or unknown>` |
| Available services | `<services or none>` |
| Subagents | `<workstreams used or unavailable>` |
| Environment limitations | `<limitations or none>` |

## 1. Executive verdict [REQUIRED]

**Scoped verdict:** `SUPPORTED_WITHIN_SCOPE / CONDITIONAL / BLOCKED / NOT_ASSESSED`

**Overall risk:** `Critical / High / Medium / Low`

**Named action classes:** `<read-only / local edits / tests / commits / PRs / external writes / deployment / destructive>`

**Bounded autonomous changes:** `Supported / Not supported / Gated`

**Broad autonomous changes:** `Supported / Not supported / Gated`

### Evidenced strengths

1. `[E-###] <strength>`
2. `[E-###] <strength>`

### Material gaps

1. `[AR-###] <gap>`
2. `[AR-###] <gap>`

### Conditions to increase autonomy

- `[AR-###] <condition and acceptance evidence>`

## 2. Architecture and trust-boundary map [REQUIRED]

| Component | Entry point | Responsibility | State or store | External boundary | Critical behavior |
| --- | --- | --- | --- | --- | --- |
| `<component>` | `<entry>` | `<scope>` | `<state>` | `<boundary>` | `<behavior>` |

### Boundary notes

- `[E-###] <package or ownership boundary>`
- `[E-###] <trust boundary or critical state transition>`

## 3. Audit coverage ledger [REQUIRED]

| Area | Applicability | Inspected | Evidence IDs | Result | Not inspected reason |
| --- | --- | --- | --- | --- | --- |
| Instructions and precedence | `<yes/no/unknown>` | `<yes/no>` | `<E-###>` | `<result>` | `<reason>` |
| Hooks and command wrappers | `<yes/no/unknown>` | `<yes/no>` | `<E-###>` | `<result>` | `<reason>` |
| CI and protected actions | `<yes/no/unknown>` | `<yes/no>` | `<E-###>` | `<result>` | `<reason>` |
| Skills and activation evaluations | `<yes/no/unknown>` | `<yes/no>` | `<E-###>` | `<result>` | `<reason>` |
| Packaging and installation | `<yes/no/unknown>` | `<yes/no>` | `<E-###>` | `<result>` | `<reason>` |
| Runtime permissions and external effects | `<yes/no/unknown>` | `<yes/no>` | `<E-###>` | `<result>` | `<reason>` |
| Bypass resistance and independent review | `<yes/no/unknown>` | `<yes/no>` | `<E-###>` | `<result>` | `<reason>` |

## 4. Guardrail matrix [REQUIRED]

Allowed values for `Present`, `Executed`, `Local`, `CI`, `Blocking`,
`Deterministic`, and `Bypass risk` are `Yes`, `No`, `Partial`, `Unknown`, and
`Not applicable`. Capability status values are `ENFORCED`, `DOCUMENTED_ONLY`,
`PARTIAL`, `GATED`, `NOT_RUN`, and `CONTRADICTED`.

| Guardrail | Applicability | Present | Executed | Local | CI | Blocking | Scope | Deterministic | Bypass risk | Evidence | Unknown owner |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `<guardrail>` | `<value>` | `<value>` | `<value>` | `<value>` | `<value>` | `<value>` | `<paths>` | `<value>` | `<value>` | `<E-###>` | `<owner>` |

## 5. Findings [REQUIRED]

Use one block per root cause. Do not duplicate the same defect in multiple
sections.

### AR-001: `<short title>` [REQUIRED]

| Field | Value |
| --- | --- |
| Classification | `CONFIRMED / LIKELY_RISK / MISSING_EVIDENCE / ENVIRONMENT_LIMITATION / NOT_APPLICABLE` |
| Severity | `Critical / High / Medium / Low` |
| Primary category | `<category>` |
| Affected scope | `<files, packages, symbols, workflows, or rules>` |
| Enforcement | `local / CI / scheduled / none / unknown` |
| Autonomy impact | `blocks / bounded-only / non-blocking` |
| Effort | `S / M / L` |
| Risk reduction | `High / Medium / Low` |

**Evidence:** `[E-###] <path:line, command, test, workflow step, or output>`

**Agent failure scenario:** `<reachable way an agent can cause the failure>`

**Current protection:** `<what exists and why it is or is not effective>`

**Bypass path:** `<realistic suppression, weakening, exclusion, or escape hatch>`

**Recommended remediation:** `<smallest corrective change>`

**Preferred mechanism:** `compiler / typed API / test / architecture check / CI / Semgrep / policy / docs`

**Required verifier:** `<command, test, owner review, runtime check, or artifact>`

## 6. Test-gap matrix [REQUIRED]

| Critical behavior | Existing evidence | Missing scenario | Risk | Recommended test | Mutation or negative path | Detection confidence |
| --- | --- | --- | --- | --- | --- | --- |
| `<behavior>` | `<E-### or none>` | `<scenario>` | `<risk>` | `<test type/name>` | `<mutation>` | `<High/Medium/Low>` |

## 7. Semgrep and enforcement recommendations [REQUIRED]

| Recommendation | Repository-specific pattern | Current gap | Preferred mechanism | Severity | Blocking behavior | Suppression policy | Rule test |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `<recommendation>` | `<pattern>` | `<gap>` | `<mechanism>` | `<severity>` | `<behavior>` | `<policy>` | `<test>` |

## 8. Agent-instruction recommendations [REQUIRED]

| Instruction area | Required rule | Evidence or finding | Mechanical enforcement | Human approval |
| --- | --- | --- | --- | --- |
| Root guidance | `<rule>` | `<E-### or AR-###>` | `<check or none>` | `<yes/no>` |
| Package guidance | `<rule>` | `<E-### or AR-###>` | `<check or none>` | `<yes/no>` |
| Change scope | `<rule>` | `<E-### or AR-###>` | `<check or none>` | `<yes/no>` |
| Evidence and verification | `<rule>` | `<E-### or AR-###>` | `<check or none>` | `<yes/no>` |
| Security and secrets | `<rule>` | `<E-### or AR-###>` | `<check or none>` | `<yes/no>` |

## 9. Validation pipeline [REQUIRED]

| Stage | Command or method | Scope | Prerequisites | Blocking | Evidence artifact | Failure meaning |
| --- | --- | --- | --- | --- | --- | --- |
| Fast local | `<command>` | `<scope>` | `<prerequisites>` | `<yes/no>` | `<artifact>` | `<meaning>` |
| Full local | `<command>` | `<scope>` | `<prerequisites>` | `<yes/no>` | `<artifact>` | `<meaning>` |
| Pull request | `<command or job>` | `<scope>` | `<prerequisites>` | `<yes/no>` | `<artifact>` | `<meaning>` |
| Scheduled deep | `<command or job>` | `<scope>` | `<prerequisites>` | `<yes/no>` | `<artifact>` | `<meaning>` |

## 10. Command and evidence log [REQUIRED]

| Evidence ID | Command or source | Classification | Executed | Exit/result | Duration | Side effects | Limitation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| E-001 | `<command or path:line>` | `SAFE / SAFE_WITH_PREREQUISITES / NOT_RUN` | `<yes/no>` | `<result>` | `<time>` | `<none or detail>` | `<none or detail>` |

## 11. Prioritized remediation plan [REQUIRED]

| Phase | Priority | Finding IDs | Remediation | Effort | Risk reduction | Dependencies | Owner type | Acceptance criteria |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Phase 0 | `<P0>` | `<AR-###>` | `<blocker>` | `<S/M/L>` | `<High/Medium/Low>` | `<dependencies>` | `<owner>` | `<criteria>` |
| Phase 1 | `<P1>` | `<AR-###>` | `<improvement>` | `<S/M/L>` | `<High/Medium/Low>` | `<dependencies>` | `<owner>` | `<criteria>` |
| Phase 2 | `<P2>` | `<AR-###>` | `<structural>` | `<S/M/L>` | `<High/Medium/Low>` | `<dependencies>` | `<owner>` | `<criteria>` |
| Phase 3 | `<P3>` | `<AR-###>` | `<advanced assurance>` | `<S/M/L>` | `<High/Medium/Low>` | `<dependencies>` | `<owner>` | `<criteria>` |

## 12. Autonomy gate [REQUIRED]

**Maximum supported level:** `0 / 1 / 2 / 3 / 4 / 5`

**Autonomy result:** `SUPPORTED_WITHIN_SCOPE / CONDITIONAL / BLOCKED / NOT_ASSESSED`

### Permitted change classes

- `<explicit bounded class>`

### Prohibited change classes

- `<explicit prohibited class>`

### Required human approvals

- `<approval owner and trigger>`

### Fail-closed conditions

- `<condition that prevents autonomous progression>`

### Evidence required to advance

- `[AR-###] <acceptance evidence>`

## 13. Residual risk and handoff [REQUIRED]

- **Confirmed findings:** `<IDs and count>`
- **Likely risks:** `<IDs and count>`
- **Missing evidence:** `<IDs and count>`
- **Environment limitations:** `<IDs and count>`
- **Not run:** `<checks and reasons>`
- **Independent review:** `<completed, unavailable, or required>`
- **Next action:** `<single concrete action>`

## Machine-checkable requirements [REQUIRED]

A consumer should reject the report when:

- the JSON markers are missing or malformed;
- `scoped_verdict` is `SUPPORTED_WITHIN_SCOPE` while a required gate is
  `GATED`, `NOT_RUN`, `FAIL`, or unknown;
- `autonomy_decision` is `ALLOWED` while any required gate is not `PASS`;
- `maximum_granted_level` exceeds `maximum_supported_level`;
- a finding lacks evidence, reachable impact, a regression or negative path,
  and a required verifier;
- an unreviewed path is not explicitly excluded with a reason;
- a command or runtime result is claimed without an execution record;
- `audit_only` is true while files changed by the audit are not `none`;
- a status uses vocabulary outside the enums declared in this template.
