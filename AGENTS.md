# Repository Instructions

Before modifying this repository:

1. Read and follow `contracts/engineering-agent-working-contract.md`.
2. Read `CONTRIBUTING.md`.
3. Keep skills portable across Codex and Claude unless a platform-specific capability requires otherwise.
4. Keep the canonical contract and `skills/engineering-working-contract/SKILL.md` synchronized.
5. Add positive and negative activation evaluations for every skill.
6. Do not add em dashes to repository text.
7. Run `python3 tooling/validate_repository.py` before reporting completion.
8. Use the commit convention defined in `config/commit_conventions.json`. The
   `commit-msg` hook and CI enforce it; read that file when a commit check
   fails instead of inventing a new format.

For changes to executable code, packaging, manifests, or workflows, also apply `skills/verify-code-change/SKILL.md`.
