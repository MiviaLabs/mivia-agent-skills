#!/usr/bin/env python3
"""Validate non-merge commits in a Git revision range."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from check_commit_message import load_conventions, validate_message


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--range",
        dest="revision_range",
        required=True,
        help="Git revision range, for example BASE..HEAD",
    )
    return parser.parse_args()


def commit_ids(revision_range: str) -> list[str]:
    left, separator, right = revision_range.partition("..")
    if separator and left and set(left) == {"0"}:
        revision_range = right or "HEAD"
    result = subprocess.run(
        ["git", "rev-list", "--no-merges", revision_range],
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line]


def commit_message(commit: str) -> str:
    result = subprocess.run(
        ["git", "show", "--format=%B", "--no-patch", commit],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def main() -> int:
    args = parse_args()
    try:
        conventions = load_conventions()
        commits = commit_ids(args.revision_range)
    except (OSError, subprocess.CalledProcessError, ValueError) as exc:
        print(f"Unable to inspect commit history: {exc}", file=sys.stderr)
        return 2

    invalid: list[tuple[str, str]] = []
    for commit in commits:
        error = validate_message(commit_message(commit), conventions)
        if error:
            invalid.append((commit, error))

    if invalid:
        print(
            f"{len(invalid)} commit(s) do not follow {Path('config/commit_conventions.json')}:\n",
            file=sys.stderr,
        )
        for commit, error in invalid:
            print(f"{commit[:12]}:", file=sys.stderr)
            print(error, file=sys.stderr)
        return 1

    print(f"Commit convention check passed for {len(commits)} non-merge commit(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
