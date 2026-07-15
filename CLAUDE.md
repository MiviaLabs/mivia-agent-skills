# Repository Instructions

@contracts/engineering-agent-working-contract.md
@CONTRIBUTING.md

- Keep skills portable across Codex and Claude unless a platform-specific capability requires otherwise.
- Keep the canonical contract and `skills/engineering-working-contract/SKILL.md` synchronized.
- Add positive and negative activation evaluations for every skill.
- Do not add em dashes to repository text.
- Run `python3 tooling/validate_repository.py` before reporting completion.
- Use the commit convention defined in `config/commit_conventions.json`. The
  `commit-msg` hook and CI enforce it; read that file when a commit check
  fails instead of inventing a new format.
- For changes to executable code, packaging, manifests, or workflows, apply `/verify-code-change`.
