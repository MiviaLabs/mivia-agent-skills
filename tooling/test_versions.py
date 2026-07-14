#!/usr/bin/env python3
"""Exercise SemVer and release-tag validation in check_versions.py."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from check_versions import load_version, validate_manifests


def write_manifest(path: Path, version: object) -> None:
    path.write_text(json.dumps({"version": version}), encoding="utf-8")


def test_valid_versions(temporary: Path) -> None:
    manifest = temporary / "plugin.json"
    for version in (
        "0.1.0",
        "1.2.3-rc.1",
        "1.2.3+build.7",
        "1.2.3-alpha-1+001.internal",
    ):
        write_manifest(manifest, version)
        assert load_version(manifest) == version


def test_invalid_versions(temporary: Path) -> None:
    manifest = temporary / "plugin.json"
    for version in (
        "01.2.3",
        "1.02.3",
        "1.2.03",
        "1.2.3-01",
        "1.2.3-alpha..1",
        "1.2.3-alpha_1",
        "1.2.3-",
        "1.2.3+",
        "1.2.3+build_1",
        "1.2.3-+build",
    ):
        write_manifest(manifest, version)
        try:
            load_version(manifest)
        except ValueError:
            continue
        raise AssertionError(f"Malformed version was accepted: {version}")


def test_exact_release_tags(temporary: Path) -> None:
    codex = temporary / "codex-plugin.json"
    claude = temporary / "claude-plugin.json"
    write_manifest(codex, "1.2.3")
    write_manifest(claude, "1.2.3")
    assert validate_manifests(codex, claude, "v1.2.3") == "1.2.3"

    version = "2.0.0-rc.2+build.11"
    write_manifest(codex, version)
    write_manifest(claude, version)

    assert validate_manifests(codex, claude, f"v{version}") == version
    for tag in ("2.0.0-rc.2+build.11", "v2.0.0", f"v{version} ", ""):
        try:
            validate_manifests(codex, claude, tag)
        except ValueError:
            continue
        raise AssertionError(f"Mismatched release tag was accepted: {tag!r}")


def test_manifest_versions_must_match(temporary: Path) -> None:
    codex = temporary / "codex-plugin.json"
    claude = temporary / "claude-plugin.json"
    write_manifest(codex, "1.0.0")
    write_manifest(claude, "1.0.0-rc.1")

    try:
        validate_manifests(codex, claude)
    except ValueError:
        return
    raise AssertionError("Mismatched manifest versions were accepted")


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary)
        test_valid_versions(path)
        test_invalid_versions(path)
        test_exact_release_tags(path)
        test_manifest_versions_must_match(path)
    print("Version tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
