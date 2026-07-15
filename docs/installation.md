# Installation and Usage

## Recommended: bootstrap one target repository

The filesystem installer is the canonical integration path when a team wants
the contract, doctrines, skills, and platform instruction files to work
together in a repository.

From a checkout of this repository, run:

```bash
python3 scripts/install.py --scope project --target both --project /path/to/repository
```

Use `python` or `py` on Windows when `python3` is unavailable. The command
updates only the target repository and creates this runtime surface:

```text
AGENTS.md                         # Codex project instructions
CLAUDE.md                         # Claude Code project instructions
.mivia-agent-skills/              # managed contract, doctrines, and manifest
.agents/skills/                   # Codex skills
.claude/skills/                   # Claude Code skills
```

The installer does not copy `articles/`, `docs/`, `examples/`, `scripts/`, or
`tooling/` into the target. Those remain source and maintainer material.

The managed block in each instruction file contains the standing contract.
Repository-specific instructions belong outside that block and remain yours to
edit. The installer rejects unmarked same-name skill collisions, backs up
changed managed content, and removes only content it owns.

Install one platform only when needed:

```bash
python3 scripts/install.py --scope project --target codex --project /path/to/repository
python3 scripts/install.py --scope project --target claude --project /path/to/repository
```

## What becomes active

Codex reads project instructions from `AGENTS.md` according to its instruction
precedence and discovers project skills under `.agents/skills/`. Claude Code
reads `CLAUDE.md` and discovers project skills under `.claude/skills/`.

The central `.mivia-agent-skills/` directory is supporting runtime state, not a
second competing instruction source. It contains the canonical contract and
two doctrines used to apply evidence and verification discipline. The managed
instruction block remains the always-on entry point.

After installation, start a fresh agent session and ask it to identify the
active instruction file, list the installed Mivia skills, and explain when the
verification, deep bug audit, generic agent readiness, and Go agent readiness
skills apply. Use the readiness skills only for named coding-agent actions and
control-plane evidence. Use the Go adapter for Go repositories; neither skill
is a general application security or production-readiness review.
Check for repository overrides such as
`AGENTS.override.md` before treating the result as complete.

For a first task, use the [skill usage examples](examples.md). Select the
closest task, open its exact skill-local example, replace the paths, commands,
permissions, and approval owners, then review the agent's executed checks and
residual-risk handoff.

## Global installation

Global installation uses the same managed bundle for the current user:

```bash
python3 scripts/install.py --scope global --target both
```

It writes Codex files under `$CODEX_HOME` (or `~/.codex`) and Claude Code files
under `~/.claude`; shared references are kept under `~/.mivia-agent-skills`.

## Updates and removal

For a filesystem installation, pull this repository and rerun the same command.
The installer updates the managed block, references, manifest, and skills as a
single transactional operation. It preserves user content outside managed
blocks and leaves backups for changed or removed managed artifacts.

Remove a project installation with:

```bash
python3 scripts/install.py --scope project --target both --project /path/to/repository --uninstall
```

Removing one target leaves the shared runtime while the other target remains.
The final target removal deletes only the managed runtime root; pre-existing
instruction files and unrelated skills remain.

## Alternative distribution paths

Plugins and ZIPs distribute skills, not repository-specific instruction files.
Use them when the target repo should not receive a managed filesystem bundle.

### Codex plugin

Add the repository as a marketplace using the Codex workflow, then install
`mivia-agentic-engineering`. Plugin installation provides the declared skills;
it does not create project `AGENTS.md` or `.mivia-agent-skills/` state.

### Claude Code plugin

```text
/plugin marketplace add MiviaLabs/mivia-agent-skills
/plugin install mivia-agentic-engineering@mivia-agent-skills
```

Start a fresh session or run `/reload-plugins`. The plugin provides namespaced
skills; it does not create project `CLAUDE.md` or the managed runtime root.

### Claude Desktop and Cowork ZIPs

Build the skill packages locally:

```bash
python3 scripts/package_claude_skills.py --output dist
```

Upload the generated skill ZIPs through the product's custom-skill flow. The
packages exclude repository evaluations and Codex metadata. The Go readiness
ZIP depends on the generic readiness ZIP; upload both when using the Go
adapter.

## Verification

Run repository checks before publishing changes:

```bash
python3 tooling/validate_repository.py
python3 tooling/test_deep_bug_audit.py
python3 tooling/test_project_bootstrap.py
python3 tooling/test_distribution.py
python3 tooling/test_packaging.py
```

For a target repository, verify from a fresh session that the agent can identify
the active instruction source, the installed platform skill directory, and the
managed contract. Test a code-change prompt and a clearly unrelated writing
prompt to check the verification skill's activation boundary.

## Platform limits

- Markdown instructions guide agents; permissions, hooks, sandboxing, and CI enforce hard boundaries.
- Plugin installation and filesystem installation are separate distribution paths.
- Evaluations remain specifications for now; repository tests validate structure, packaging, and filesystem behavior.

## Official platform references

- [OpenAI AGENTS.md guidance](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- [OpenAI skills guidance](https://learn.chatgpt.com/docs/build-skills)
- [Anthropic Claude Code skills](https://code.claude.com/docs/en/skills)
- [Anthropic Claude Code plugins](https://code.claude.com/docs/en/plugins)
