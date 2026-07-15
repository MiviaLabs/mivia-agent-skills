#!/usr/bin/env python3
"""Test interpreter-environment handling in the shared check runner."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def load_runner():
    repository = Path(__file__).resolve().parents[1]
    source = repository / "scripts/run_checks.py"
    spec = importlib.util.spec_from_file_location("run_checks_under_test", source)
    if spec is None or spec.loader is None:
        raise AssertionError(f"Could not load check runner from {source}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_python_bin_dir_preserves_selected_interpreter_path() -> None:
    runner = load_runner()
    original = sys.executable
    try:
        sys.executable = "/tmp/mivia-docs-venv/bin/python"
        assert runner.python_bin_dir() == Path("/tmp/mivia-docs-venv/bin")
    finally:
        sys.executable = original


def main() -> int:
    test_python_bin_dir_preserves_selected_interpreter_path()
    print("Check runner tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
