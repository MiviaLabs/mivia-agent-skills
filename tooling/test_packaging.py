#!/usr/bin/env python3
"""Exercise generalized Claude skill packaging with a temporary fixture."""

from __future__ import annotations

import importlib.util
import tempfile
import zipfile
from pathlib import Path


def load_packager(repository: Path):
    source = repository / "scripts/package_claude_skills.py"
    spec = importlib.util.spec_from_file_location("package_claude_skills", source)
    if spec is None or spec.loader is None:
        raise AssertionError(f"Could not load packager from {source}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_packages_all_supported_fixture_entries(repository: Path) -> None:
    packager = load_packager(repository)
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        skill = root / "fixture-skill"
        output = root / "packages"
        (skill / "templates").mkdir(parents=True)
        (skill / "references").mkdir()
        (skill / "scripts").mkdir()
        (skill / "assets").mkdir()
        (skill / "agents").mkdir()
        (skill / "evaluations").mkdir()
        (skill / "SKILL.md").write_bytes(b"# Fixture skill\n")
        (skill / "support.txt").write_bytes(b"included support\n")
        (skill / "templates/prompt.txt").write_bytes(b"template\n")
        (skill / "references/taxonomy.md").write_bytes(b"reference\n")
        (skill / "references/examples").mkdir()
        (skill / "references/examples/01-example.md").write_bytes(b"example\n")
        (skill / "scripts/check.py").write_bytes(b"print('check')\n")
        (skill / "assets/example.txt").write_bytes(b"asset\n")
        (skill / "agents/openai.yaml").write_bytes(b"metadata\n")
        (skill / "evaluations/positive.json").write_bytes(b"{}\n")

        archive_path = packager.package_skill(skill, output)

        assert archive_path == output / "fixture-skill.zip"
        with zipfile.ZipFile(archive_path) as archive:
            entries = set(archive.namelist())
            assert entries == {
                "fixture-skill/skill.md",
                "fixture-skill/support.txt",
                "fixture-skill/templates/prompt.txt",
                "fixture-skill/references/taxonomy.md",
                "fixture-skill/references/examples/01-example.md",
                "fixture-skill/scripts/check.py",
                "fixture-skill/assets/example.txt",
                "fixture-skill/evaluations/positive.json",
            }
            assert archive.read("fixture-skill/skill.md") == b"# Fixture skill\n"
            assert archive.read("fixture-skill/support.txt") == b"included support\n"
            assert archive.read("fixture-skill/templates/prompt.txt") == b"template\n"
            assert archive.read("fixture-skill/references/taxonomy.md") == b"reference\n"
            assert archive.read("fixture-skill/references/examples/01-example.md") == b"example\n"
            assert archive.read("fixture-skill/scripts/check.py") == b"print('check')\n"
            assert archive.read("fixture-skill/assets/example.txt") == b"asset\n"
            assert archive.read("fixture-skill/evaluations/positive.json") == b"{}\n"


def test_packager_removes_obsolete_archives(repository: Path) -> None:
    packager = load_packager(repository)
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        skill = root / "fixture-skill"
        output = root / "packages"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text("# Fixture skill\n", encoding="utf-8")
        output.mkdir()
        (output / "deep-bug-audit.zip").write_bytes(b"obsolete")
        packager.remove_obsolete_archives(output, {"fixture-skill.zip"})
        assert not (output / "deep-bug-audit.zip").exists()


def main() -> int:
    repository = Path(__file__).resolve().parents[1]
    test_packages_all_supported_fixture_entries(repository)
    print("Packaging tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
