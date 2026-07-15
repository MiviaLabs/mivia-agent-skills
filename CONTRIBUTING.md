# Contributing

Contributions should improve practical agentic engineering workflows, not add generic prompt fragments.

## What belongs here

- focused agent skills with clear activation conditions and outputs;
- engineering doctrines grounded in real delivery problems;
- workflow guidance covering planning, implementation, verification, review, or delivery;
- evaluations that expose weak, unsafe, or incorrect agent behavior;
- articles that explain the mechanism behind a practice;
- installation and validation improvements that make the assets easier to use safely.

## What does not belong here

- large untested prompt collections;
- duplicated platform-specific skills without a real capability difference;
- speculative frameworks without practical use;
- instructions that cannot be evaluated or verified;
- vendor marketing copied into repository guidance;
- claims that exceed the available evidence.

## Pull requests

A contribution should state:

1. the problem it addresses;
2. the intended user or agent;
3. how the behavior can be verified;
4. known limitations or platform differences;
5. whether the change affects installation, manifests, or release packages.

Keep changes focused. Do not mix unrelated cleanup with a new doctrine, skill, or article.

## Skill requirements

Every skill must include:

- a concise `SKILL.md`;
- clear activation and non-activation conditions;
- required inputs when applicable;
- an ordered procedure;
- expected output;
- failure and escalation behavior;
- at least one positive and one negative activation evaluation.

Descriptions must be specific enough for reliable implicit invocation and short enough for platform skill indexes.

## Cross-platform rules

- Keep the core skill compatible with the open Agent Skills structure.
- Put OpenAI-specific interface metadata under `agents/openai.yaml`.
- Do not add Claude-only frontmatter unless the behavior cannot be represented portably.
- Keep scripts optional unless deterministic behavior or external tooling is required.
- Do not grant broad tool permissions by default.

## Validation

Run:

```bash
python3 tooling/validate_repository.py
```

When changing packaging logic, also run:

```bash
python3 scripts/package_claude_skills.py --output /tmp/mivia-skill-packages
```

## Local validation hooks

Configure the tracked hooks once per checkout:

```bash
python3 scripts/install_hooks.py
python3 -m venv .venv
.venv/bin/python -m pip install --requirement requirements/docs.txt
```

The pre-commit hook runs the repository checks and, when its selected Python
interpreter can import MkDocs, the full documentation build and generated-site
checks. The pre-push hook always runs those checks plus the documentation
build. If the documentation tooling is missing, the pre-push hook fails closed
instead of allowing a push that CI cannot build. Git hooks can still be bypassed with
`--no-verify`, so protected branches and required GitHub checks remain the
server-side authority.

## Commit messages

Commit messages use the convention in `config/commit_conventions.json`. Use the
form `<type>[optional scope][!]: <description>`, for example `feat: add a
skill` or `fix(hooks): explain invalid commits`. The tracked `commit-msg` hook
and CI read the same file, so update that file when the allowed types change.

## Writing

Use direct, plain language. Lead with the conclusion. Avoid hype, filler, defensive disclaimers, and unnecessary jargon. Use normal hyphens instead of em dashes.
