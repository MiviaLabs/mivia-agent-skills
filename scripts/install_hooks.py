#!/usr/bin/env python3
"""Configure this checkout to use its tracked Git validation hooks."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOOKS = (
    ROOT / ".githooks/pre-commit",
    ROOT / ".githooks/commit-msg",
    ROOT / ".githooks/pre-push",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify the local hook configuration without changing it",
    )
    return parser.parse_args()


def configured_path() -> str | None:
    result = subprocess.run(
        ["git", "config", "--local", "--get", "core.hooksPath"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if result.returncode:
        return None
    return result.stdout.strip()


def main() -> int:
    args = parse_args()
    missing = [str(path.relative_to(ROOT)) for path in HOOKS if not path.is_file()]
    if missing:
        print(f"Missing tracked hook(s): {', '.join(missing)}", file=sys.stderr)
        return 1

    current = configured_path()
    if args.check:
        if current != ".githooks":
            print(
                f"Git hooks are not configured: core.hooksPath={current!r}",
                file=sys.stderr,
            )
            return 1
        print("Git hooks are configured: core.hooksPath=.githooks")
        return 0

    result = subprocess.run(
        ["git", "config", "--local", "core.hooksPath", ".githooks"],
        cwd=ROOT,
    )
    if result.returncode:
        return result.returncode

    print("Configured Git hooks: core.hooksPath=.githooks")
    print("pre-commit runs repository checks and available MkDocs checks before every commit.")
    print("commit-msg enforces config/commit_conventions.json.")
    print("pre-push runs repository checks and the documentation build.")
    print("Install documentation tooling in this checkout before pushing:")
    print("  python3 -m venv .venv")
    print("  .venv/bin/python -m pip install --requirement requirements/docs.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
