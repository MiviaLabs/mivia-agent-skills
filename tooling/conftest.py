"""Pytest fixtures for tooling test modules.

Test modules in this directory are designed as standalone scripts invoked via
``python tooling/test_X.py`` (entry point: ``main()``).  This conftest makes
the same test functions runnable under ``pytest`` by providing the fixtures
that main() passes positionally.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def root() -> Path:
    """Repository root (one directory above tooling/)."""
    return Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def repository(root: Path) -> Path:
    """Alias for root, matching the parameter name used by distribution and
    packaging test modules."""
    return root


@pytest.fixture()
def temporary() -> Path:
    """Per-test temporary directory, cleaned up after each test."""
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)
