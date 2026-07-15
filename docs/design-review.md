# Design Review and Known Gaps

This document records the main challenges applied to the repository design and the resulting decisions.

## Challenge: one large global prompt

**Finding:** Too broad.

A single file mixes standing judgment, task procedures, repository facts, and hard controls. Those concerns have different scopes.

**Decision:** Keep a compact canonical contract, move repeatable workflows into skills, keep repository facts in `AGENTS.md` or `CLAUDE.md`, and enforce hard boundaries outside Markdown.

## Challenge: one rigid evidence hierarchy

**Finding:** Incorrect for some decisions.

Runtime behavior is strong evidence of what the system currently does, but it is not automatically evidence of what the system should do. Tests and documentation can also be stale or wrong.

**Decision:** Separate intended-behavior evidence from current-behavior evidence and reconcile conflicts explicitly.

## Challenge: root cause before every change

**Finding:** Too absolute.

Production incidents sometimes require containment before the full root cause is known.

**Decision:** Require understanding of the failure or invariant before selecting a fix, while allowing explicit mitigation with remaining root cause work documented.

## Challenge: verification proves correctness

**Finding:** False.

No practical verification process proves the absence of defects.

**Decision:** Define `PASS` as success within the executed scope. Require skipped checks and residual risk to remain visible.

## Challenge: independent review for high-risk work

**Finding:** Correct direction, weak without a boundary.

**Decision:** Call out security, privacy, migrations, concurrency, destructive actions, and broad compatibility changes as categories that justify independent review or explicit approval.

## Challenge: portable skills are automatically portable

**Finding:** Not fully true.

Codex, Claude Code, and Claude Desktop use similar skill structures but different installation and packaging paths. Platform-specific metadata can also diverge.

**Decision:** Keep one portable `SKILL.md`, isolate OpenAI interface metadata under `agents/openai.yaml`, provide dual plugin manifests, and generate Claude Desktop ZIPs from the same sources.

## Challenge: static evaluation files make a skill tested

**Finding:** Incomplete.

Evaluation cases are specifications until a runner executes them.

**Decision:** Describe them as activation and behavior cases, validate their structure in CI, and avoid claiming model-level performance until comparative runs are recorded.

## Challenge: plugin packaging makes the repository installable immediately

**Finding:** Not by itself.

Marketplace installation by repository name depends on the manifests being present in the repository's default branch. Claude Desktop ZIPs also require either a tagged release or a local packaging step.

**Decision:** Document both conditions explicitly, validate package structure, and generate upload-ready ZIPs during tagged releases.

## Current known gaps

- No model-level benchmark results are published yet.
- The evaluation files are validated structurally but are not automatically executed against Codex or Claude.
- The plugin packages have not yet been submitted to the public OpenAI or Anthropic directories.
- Installation workflows still need real-user testing on macOS, Windows, and Linux.
- Marketplace installation by repository name becomes available only after the plugin manifests are present in the default branch.
- Claude Desktop release downloads become available only after the first tagged release.
- The working contract can still conflict with repository-specific instructions if teams write ambiguous overrides.
- Hard controls remain the responsibility of the consuming environment.
- The Go agent-readiness adapter depends on the generic agent-readiness skill when skills are distributed as separate ZIPs; both packages must be installed together.

These are explicit limits, not hidden implementation details.
