#!/usr/bin/env python3
"""Validate one commit message against the repository commit convention."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONVENTIONS = ROOT / "config/commit_conventions.json"


def load_conventions() -> dict[str, object]:
    data = json.loads(CONVENTIONS.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Commit convention file must contain an object: {CONVENTIONS}")
    types = data.get("types")
    if (
        not isinstance(types, list)
        or not types
        or any(not isinstance(value, str) or not value for value in types)
        or len(set(types)) != len(types)
    ):
        raise ValueError(f"Commit convention types must be a unique non-empty array: {CONVENTIONS}")
    return data


def validate_subject(subject: str, conventions: dict[str, object]) -> str | None:
    generated_prefixes = conventions.get("allow_generated_prefixes", [])
    if any(
        isinstance(prefix, str) and subject.startswith(prefix)
        for prefix in generated_prefixes
    ):
        return None

    types = conventions["types"]
    assert isinstance(types, list)
    type_pattern = "|".join(re.escape(value) for value in types)
    breaking = "!?" if conventions.get("allow_breaking_marker") else ""
    pattern = re.compile(
        rf"^(?P<type>{type_pattern})(?:\((?P<scope>[^()\r\n]+)\))?{breaking}: (?P<description>\S.*)$"
    )
    if pattern.fullmatch(subject) is not None:
        return None

    allowed = ", ".join(types)
    return (
        "Commit message does not follow the repository convention.\n"
        f"Read {CONVENTIONS.relative_to(ROOT)} and use: "
        "<type>[optional scope][!]: <description>\n"
        f"Allowed types: {allowed}\n"
        "Examples: feat: add project bootstrap; fix(hooks): explain invalid commits"
    )


def validate_message(message: str, conventions: dict[str, object] | None = None) -> str | None:
    conventions = conventions or load_conventions()
    subject = message.splitlines()[0] if message.splitlines() else ""
    return validate_subject(subject, conventions)


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if len(args) != 1:
        print(f"Usage: {Path(sys.argv[0]).name} <commit-message-file>", file=sys.stderr)
        return 2

    try:
        conventions = load_conventions()
        message = Path(args[0]).read_text(encoding="utf-8")
        error = validate_message(message, conventions)
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        print(f"Unable to validate commit message: {exc}", file=sys.stderr)
        return 2

    if error:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
