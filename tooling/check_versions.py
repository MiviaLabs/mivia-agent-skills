#!/usr/bin/env python3
"""Check plugin manifest versions and optional release tag alignment."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_NUMERIC_IDENTIFIER = r"(?:0|[1-9][0-9]*)"
_NON_NUMERIC_IDENTIFIER = r"[0-9A-Za-z-]*[A-Za-z-][0-9A-Za-z-]*"
_PRERELEASE_IDENTIFIER = rf"(?:{_NUMERIC_IDENTIFIER}|{_NON_NUMERIC_IDENTIFIER})"
_BUILD_IDENTIFIER = r"[0-9A-Za-z-]+"
SEMVER = re.compile(
    rf"(?:{_NUMERIC_IDENTIFIER})\.(?:{_NUMERIC_IDENTIFIER})\.(?:{_NUMERIC_IDENTIFIER})"
    rf"(?:-(?:{_PRERELEASE_IDENTIFIER})(?:\.(?:{_PRERELEASE_IDENTIFIER}))*)?"
    rf"(?:\+(?:{_BUILD_IDENTIFIER})(?:\.(?:{_BUILD_IDENTIFIER}))*)?"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", help="Release tag, for example v0.1.0")
    return parser.parse_args()


def load_version(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    version = data.get("version")
    if not isinstance(version, str) or not SEMVER.fullmatch(version):
        raise ValueError(f"Invalid semantic version in {path}: {version!r}")
    return version


def validate_manifests(
    codex_manifest: Path, claude_manifest: Path, tag: str | None = None
) -> str:
    codex = load_version(codex_manifest)
    claude = load_version(claude_manifest)
    if codex != claude:
        raise ValueError(f"Plugin versions differ: Codex={codex}, Claude={claude}")

    if tag is not None:
        expected = f"v{codex}"
        if tag != expected:
            raise ValueError(
                f"Release tag {tag!r} does not match manifest version {expected!r}"
            )
    return codex


def main() -> int:
    args = parse_args()
    root = Path(__file__).resolve().parents[1]

    try:
        codex = validate_manifests(
            root / ".codex-plugin/plugin.json",
            root / ".claude-plugin/plugin.json",
            args.tag,
        )
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"Version check failed: {exc}", file=sys.stderr)
        return 1

    print(f"Plugin version check passed: {codex}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
