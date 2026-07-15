#!/usr/bin/env python3
"""Check the tracked Git hooks and their shared validation plan."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    pre_commit = root / ".githooks/pre-commit"
    commit_msg = root / ".githooks/commit-msg"
    pre_push = root / ".githooks/pre-push"
    runner = root / "scripts/run_checks.py"

    assert pre_commit.is_file()
    assert commit_msg.is_file()
    assert pre_push.is_file()
    assert runner.is_file()
    assert "--suite pre-commit" in pre_commit.read_text(encoding="utf-8")
    assert "tooling/check_commit_message.py" in commit_msg.read_text(encoding="utf-8")
    assert "--suite all" in pre_push.read_text(encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(runner), "--suite", "all", "--print-plan"],
        cwd=root,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stderr
    for expected in (
        "tooling/validate_repository.py",
        "tooling/test_project_bootstrap.py",
        "tooling/test_hooks.py",
        "tooling/build_docs_site.py",
        "tooling/test_docs_site.py",
        "scripts/package_claude_skills.py",
    ):
        assert expected in result.stdout

    print("Git hook tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
