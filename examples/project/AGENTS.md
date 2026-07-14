# Repository Instructions

This file is repository-owned configuration. Install the Mivia runtime first:

```bash
python3 /path/to/mivia-agent-skills/scripts/install.py --scope project --target both --project .
```

The installer adds the managed standing contract block. Edit the sections below
and keep repository-specific instructions outside that block. Replace every
`<REPLACE_ME: ...>` value before relying on this file.

## Repository context

- Architecture: <REPLACE_ME: describe the system boundaries>
- Primary languages and frameworks: <REPLACE_ME: list them>
- Important service or package boundaries: <REPLACE_ME: name packages/services>
- Security-sensitive paths: <REPLACE_ME: identify paths and handling rules>

## Commands

- Setup: <REPLACE_ME: command>
- Focused test: <REPLACE_ME: command>
- Full test: <REPLACE_ME: command>
- Lint: <REPLACE_ME: command or not applicable>
- Type-check: <REPLACE_ME: command or not applicable>
- Build: <REPLACE_ME: command or not applicable>
- Run: <REPLACE_ME: command>

## Engineering rules

- Definition of done: <REPLACE_ME: concrete acceptance criteria>
- Dependency policy: <REPLACE_ME: approval and update rules>
- Backward compatibility requirements: <REPLACE_ME: compatibility contract>
- Migration rules: <REPLACE_ME: migration and rollback requirements>
- Required reviewers or approvals: <REPLACE_ME: owners and gates>

## Verification

Run the smallest relevant check first, then expand according to risk and blast radius. Report anything that could not be verified.
