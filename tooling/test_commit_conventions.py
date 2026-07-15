#!/usr/bin/env python3
"""Test the shared commit convention and its local validation entry point."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


def run_checker(root: Path, message: str) -> subprocess.CompletedProcess[str]:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as handle:
        handle.write(message)
        path = Path(handle.name)
    try:
        return subprocess.run(
            [sys.executable, str(root / "tooling/check_commit_message.py"), str(path)],
            cwd=root,
            capture_output=True,
            text=True,
        )
    finally:
        path.unlink()


def run_git(repository: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repository), *args],
        check=True,
        capture_output=True,
        text=True,
    )


def test_history_checker(root: Path, temporary: Path) -> None:
    repository = temporary / "history"
    repository.mkdir()
    run_git(repository, "init", "-q")
    run_git(repository, "config", "user.name", "Commit Test")
    run_git(repository, "config", "user.email", "commit-test@example.com")
    (repository / "file.txt").write_text("one\n", encoding="utf-8")
    run_git(repository, "add", "file.txt")
    run_git(repository, "-c", "commit.gpgsign=false", "commit", "-qm", "feat: initial")
    (repository / "file.txt").write_text("two\n", encoding="utf-8")
    run_git(repository, "add", "file.txt")
    run_git(repository, "-c", "commit.gpgsign=false", "commit", "-qm", "bad message")

    script = root / "tooling/check_commit_history.py"
    invalid = subprocess.run(
        [sys.executable, str(script), "--range", "HEAD~1..HEAD"],
        cwd=repository,
        capture_output=True,
        text=True,
    )
    assert invalid.returncode == 1
    assert "config/commit_conventions.json" in invalid.stderr

    valid = subprocess.run(
        [sys.executable, str(script), "--range", "HEAD~1"],
        cwd=repository,
        capture_output=True,
        text=True,
    )
    assert valid.returncode == 0, valid.stderr


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    config_path = root / "config/commit_conventions.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    assert isinstance(config["types"], list)
    assert config["types"] == sorted(config["types"])

    for message in (
        "feat: add a capability\n",
        "fix(hooks)!: reject invalid commit messages\n\nDetails\n",
        "Merge branch 'main'\n",
        "Revert \"feat: add a capability\"\n",
    ):
        result = run_checker(root, message)
        assert result.returncode == 0, result.stderr

    invalid = run_checker(root, "Add a capability\n")
    assert invalid.returncode == 1
    assert "config/commit_conventions.json" in invalid.stderr
    assert "Allowed types:" in invalid.stderr

    empty = run_checker(root, "\n")
    assert empty.returncode == 1

    with tempfile.TemporaryDirectory() as temporary:
        test_history_checker(root, Path(temporary))

    print("Commit convention tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
