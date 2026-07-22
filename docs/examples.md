# Skill usage examples

These are adaptable request templates for the first task after installation.
They show when a skill applies, what context to provide, what evidence to ask
for, and how to read the handoff. They are not executable transcripts and do
not claim that an agent ran the commands or created the artifacts shown in the
templates.

## First-use sequence

1. Choose a distribution path in [Installation and usage](installation.md).
2. Install the filesystem runtime, configure the relevant project instruction
   file, or install a plugin or ZIP through its product flow.
3. Start a fresh agent session and confirm the active instruction source and
   installed skill directory.
4. Choose the closest task below and open the exact example file.
5. Replace every placeholder before sending the request.
6. Review the handoff, executed checks, residual risk, and approval gate.

Filesystem installation proves the skill-local `references/` tree is copied to
the target. Claude ZIP packaging proves the same tree is available in the
archive. Actual Codex Desktop and Claude Code plugin installation remains a
separate product-level check.

## Choose by task

| Task | Skill | Example |
| --- | --- | --- |
| Engineering change with a concurrency invariant | [Engineering working contract](../skills/engineering-working-contract/SKILL.md) | [Concurrency fix](../skills/engineering-working-contract/references/examples/01-concurrency-fix.md) |
| Incident mitigation before root cause is complete | [Engineering working contract](../skills/engineering-working-contract/SKILL.md) | [Production containment](../skills/engineering-working-contract/references/examples/02-production-containment.md) |
| Focused parser regression verification | [Verify code change](../skills/verify-code-change/SKILL.md) | [Parser regression pass](../skills/verify-code-change/references/examples/01-parser-regression-pass.md) |
| Migration verification with a missing deployment gate | [Verify code change](../skills/verify-code-change/SKILL.md) | [Partial migration verification](../skills/verify-code-change/references/examples/02-database-migration-partial.md) |
| Current diff or repository bug hunt | [Bug audit](../skills/bug-audit/SKILL.md) | [Evaluation evidence](../skills/bug-audit/evaluations/README.md) |
| Named authorization and persistence paths | [Bug audit](../skills/bug-audit/SKILL.md) | [Evaluation evidence](../skills/bug-audit/evaluations/README.md) |
| Bounded coding-agent action review | [Agent readiness audit](../skills/agent-readiness-audit/SKILL.md) | [Bounded action readiness](../skills/agent-readiness-audit/references/examples/01-bounded-action-readiness.md) |
| Repository-wide control-plane audit | [Agent readiness audit](../skills/agent-readiness-audit/SKILL.md) | [Gated repository readiness](../skills/agent-readiness-audit/references/examples/02-repository-readiness-gated.md) |
| Go repository control-plane and autonomy review | [Go agent readiness audit](../skills/agent-readiness-audit-go/SKILL.md) | [Repository autonomy readiness](../skills/agent-readiness-audit-go/references/examples/01-repository-autonomy-readiness.md) |
| Missing runtime or permission evidence in Go | [Go agent readiness audit](../skills/agent-readiness-audit-go/SKILL.md) | [Gated runtime readiness](../skills/agent-readiness-audit-go/references/examples/02-agent-runtime-readiness-gated.md) |
| README visual with available image generation | [Mivia image generation](../skills/mivia-image-generation/SKILL.md) | [README banner](../skills/mivia-image-generation/references/examples/01-readme-banner.md) |
| Image request when a capability or source is unavailable | [Mivia image generation](../skills/mivia-image-generation/SKILL.md) | [Capability unavailable](../skills/mivia-image-generation/references/examples/02-image-capability-unavailable.md) |

## Authoring rules

Every example must:

- name the trigger and the boundary it exercises;
- use visible placeholders in `Replace before running`;
- state the required repository context and approval owner;
- label any handoff as illustrative unless it contains evidence from the
  current task;
- describe evidence to obtain instead of inventing results;
- state failure, escalation, and capability-unavailable behavior;
- stay shorter than the owning skill procedure and avoid copying it.

The examples are documentation specifications. They do not execute model
evaluations, prove code correctness, or replace repository tests, permissions,
hooks, CI, or human approval.
