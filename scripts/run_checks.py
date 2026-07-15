#!/usr/bin/env python3
"""Run the repository checks shared by CI and local Git hooks."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REPOSITORY_CHECKS = (
    ("repository validation", "tooling/validate_repository.py"),
    ("version consistency", "tooling/check_versions.py"),
    ("version tests", "tooling/test_versions.py"),
    ("example tests", "tooling/test_examples.py"),
    ("deep bug audit tests", "tooling/test_deep_bug_audit.py"),
    ("distribution tests", "tooling/test_distribution.py"),
    ("project bootstrap tests", "tooling/test_project_bootstrap.py"),
    ("packaging tests", "tooling/test_packaging.py"),
    ("commit convention tests", "tooling/test_commit_conventions.py"),
    ("hook tests", "tooling/test_hooks.py"),
)
PRE_COMMIT_CHECKS = REPOSITORY_CHECKS
DOCS_CHECKS = (
    ("documentation build", "tooling/build_docs_site.py"),
    ("documentation site tests", "tooling/test_docs_site.py"),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--suite",
        choices=("pre-commit", "repository", "docs", "all"),
        required=True,
    )
    parser.add_argument(
        "--print-plan",
        action="store_true",
        help="Print the commands without running them",
    )
    return parser.parse_args()


def suites(name: str) -> list[tuple[str, str]]:
    if name in {"pre-commit", "repository"}:
        return list(REPOSITORY_CHECKS)
    if name == "docs":
        return list(DOCS_CHECKS)
    return [*REPOSITORY_CHECKS, *DOCS_CHECKS]


def command_for(relative_script: str) -> list[str]:
    return [sys.executable, str(ROOT / relative_script)]


def print_plan(checks: list[tuple[str, str]]) -> None:
    for label, relative_script in checks:
        display_command = [sys.executable, (ROOT / relative_script).as_posix()]
        print(f"{label}: {' '.join(display_command)}")
    if any(relative_script == "tooling/validate_repository.py" for _, relative_script in checks):
        print(
            "Claude skill packaging: "
            f"{sys.executable} {(ROOT / 'scripts/package_claude_skills.py').as_posix()} "
            f"--output {(ROOT / 'dist').as_posix()}"
        )


def run_check(label: str, relative_script: str) -> int:
    command = command_for(relative_script)
    environment = os.environ.copy()
    current_python_bin = str(Path(sys.executable).resolve().parent)
    environment["PATH"] = os.pathsep.join(
        [current_python_bin, environment.get("PATH", "")]
    ).rstrip(os.pathsep)
    if relative_script == "tooling/test_docs_site.py":
        environment["PYTHONPATH"] = os.pathsep.join(
            [str(ROOT / "tooling"), environment.get("PYTHONPATH", "")]
        ).rstrip(os.pathsep)

    print(f"\n==> {label}")
    completed = subprocess.run(command, cwd=ROOT, env=environment)
    if completed.returncode:
        print(f"FAILED: {label} (exit {completed.returncode})", file=sys.stderr)
    return completed.returncode


def run_repository_checks(checks: list[tuple[str, str]]) -> int:
    for label, relative_script in checks:
        result = run_check(label, relative_script)
        if result:
            return result

    package_command = [
        sys.executable,
        str(ROOT / "scripts/package_claude_skills.py"),
        "--output",
        str(ROOT / "dist"),
    ]
    print("\n==> Claude skill packaging")
    completed = subprocess.run(package_command, cwd=ROOT)
    if completed.returncode:
        print(
            f"FAILED: Claude skill packaging (exit {completed.returncode})",
            file=sys.stderr,
        )
    return completed.returncode


def main() -> int:
    args = parse_args()
    selected = suites(args.suite)
    if args.print_plan:
        print_plan(selected)
        return 0

    if args.suite == "docs":
        for label, relative_script in selected:
            result = run_check(label, relative_script)
            if result:
                return result
        return 0

    if args.suite == "all":
        result = run_repository_checks(REPOSITORY_CHECKS)
        if result:
            return result
        for label, relative_script in DOCS_CHECKS:
            result = run_check(label, relative_script)
            if result:
                return result
        return 0

    return run_repository_checks(selected)


if __name__ == "__main__":
    raise SystemExit(main())
