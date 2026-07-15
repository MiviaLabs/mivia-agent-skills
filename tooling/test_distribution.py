#!/usr/bin/env python3
"""Exercise installation, removal, and Claude ZIP packaging in isolation."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


def run(
    command: list[str], *, env: dict[str, str] | None = None, check: bool = True
) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(command, env=env, text=True, capture_output=True)
    if check and completed.returncode != 0:
        raise RuntimeError(
            f"Command failed: {' '.join(command)}\n{completed.stdout}\n{completed.stderr}"
        )
    return completed


def assert_managed_install(project: Path) -> None:
    assert "BEGIN MIVIA" in (project / "AGENTS.md").read_text(encoding="utf-8")
    assert "BEGIN MIVIA" in (project / "CLAUDE.md").read_text(encoding="utf-8")
    assert (project / ".agents/skills/engineering-working-contract/.mivia-managed").exists()
    assert (project / ".claude/skills/verify-code-change/.mivia-managed").exists()
    assert (project / ".agents/skills/deep-bug-audit/references/bug-taxonomy.md").exists()
    assert (project / ".agents/skills/deep-bug-audit/scripts/audit_efficiency_score.py").exists()
    assert (project / ".claude/skills/deep-bug-audit/references/bug-taxonomy.md").exists()
    assert (project / ".claude/skills/deep-bug-audit/scripts/audit_efficiency_score.py").exists()


def tree_state(root: Path) -> dict[str, tuple[str, bytes | None]]:
    state: dict[str, tuple[str, bytes | None]] = {}
    for path in sorted(root.rglob("*")):
        relative = str(path.relative_to(root))
        if path.is_dir():
            state[relative] = ("directory", None)
        elif path.is_file():
            state[relative] = ("file", path.read_bytes())
        else:
            raise AssertionError(f"Unsupported test path type: {path}")
    return state


def example_files(repository: Path) -> dict[str, bytes]:
    files = {}
    for skill in sorted((repository / "skills").iterdir()):
        examples = skill / "references" / "examples"
        if not examples.is_dir():
            continue
        for path in sorted(examples.rglob("*")):
            if path.is_file():
                files[f"{skill.name}/references/examples/{path.relative_to(examples)}"] = (
                    path.read_bytes()
                )
    return files


def assert_installed_examples(repository: Path, project: Path, target: str) -> None:
    source_files = example_files(repository)
    installed_root = project / f".{target}/skills"
    installed_files = {}
    for relative in source_files:
        path = installed_root / relative
        assert path.is_file(), path
        installed_files[relative] = path.read_bytes()
    assert installed_files == source_files


def test_both_transaction_rollback(repository: Path, temporary: Path) -> None:
    installer = repository / "scripts/install.py"
    project = temporary / "rollback-project"
    project.mkdir()
    (project / "AGENTS.md").write_text("# Existing Codex\n", encoding="utf-8")
    (project / "CLAUDE.md").write_text("# Existing Claude\n", encoding="utf-8")

    codex_skills = project / ".agents/skills"
    codex_skills.mkdir(parents=True)
    existing_skill = codex_skills / "engineering-working-contract"
    existing_skill.mkdir()
    (existing_skill / "SKILL.md").write_text("old skill\n", encoding="utf-8")
    (existing_skill / ".mivia-managed").write_text(
        "MiviaLabs/mivia-agent-skills\n", encoding="utf-8"
    )
    registry = codex_skills / ".mivia-agent-skills.json"
    registry.write_text(
        json.dumps(
            {
                "source": "MiviaLabs/mivia-agent-skills",
                "skills": ["engineering-working-contract"],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    # The first target can mutate, while the second target fails at its skills parent.
    claude_skills = project / ".claude/skills"
    claude_skills.parent.mkdir()
    claude_skills.write_text("user-owned path\n", encoding="utf-8")
    before = tree_state(project)

    result = run(
        [
            sys.executable,
            str(installer),
            "--scope",
            "project",
            "--target",
            "both",
            "--project",
            str(project),
        ],
        check=False,
    )
    assert result.returncode == 1
    assert "Installation failed:" in result.stderr
    assert tree_state(project) == before
    assert not list(project.rglob("*.mivia-backup-*"))


def test_both_uninstall_transaction_rollback(repository: Path, temporary: Path) -> None:
    installer = repository / "scripts/install.py"
    project = temporary / "rollback-uninstall-project"
    project.mkdir()
    command = [
        sys.executable,
        str(installer),
        "--scope",
        "project",
        "--target",
        "both",
        "--project",
        str(project),
    ]
    run(command)

    claude_instruction = project / "CLAUDE.md"
    claude_instruction.unlink()
    claude_instruction.mkdir()
    (claude_instruction / "user-file.txt").write_text("preserve\n", encoding="utf-8")
    before = tree_state(project)

    result = run(command + ["--uninstall"], check=False)
    assert result.returncode == 1
    assert "Installation failed:" in result.stderr
    assert tree_state(project) == before
    assert not list(project.rglob("*.mivia-backup-*"))


def test_installer(repository: Path, temporary: Path) -> None:
    project = temporary / "project"
    project.mkdir()
    (project / ".agents/skills/verify-code-change").mkdir(parents=True)

    codex_file = project / "AGENTS.md"
    claude_file = project / "CLAUDE.md"
    codex_file.write_text("# Existing Codex\n\nKeep this.\n", encoding="utf-8")
    claude_file.write_text("# Existing Claude\n\nKeep this.\n", encoding="utf-8")
    collision = project / ".agents/skills/verify-code-change/custom.txt"
    collision.write_text("Existing user skill\n", encoding="utf-8")

    installer = repository / "scripts/install.py"
    command = [
        sys.executable,
        str(installer),
        "--scope",
        "project",
        "--target",
        "both",
        "--project",
        str(project),
    ]

    collision_result = run(command, check=False)
    assert collision_result.returncode == 1
    assert "Unmarked skill collision" in collision_result.stderr
    assert collision.read_text(encoding="utf-8") == "Existing user skill\n"
    shutil.rmtree(project / ".agents/skills/verify-code-change")
    run(command)
    assert_managed_install(project)
    assert_installed_examples(repository, project, "agents")
    assert_installed_examples(repository, project, "claude")

    run(command)
    assert_managed_install(project)
    assert not list(
        (project / ".agents/skills").glob("engineering-working-contract.mivia-backup-*")
    )

    reinstall_note = project / ".agents/skills/engineering-working-contract/user-note.md"
    reinstall_note.write_text("Keep this reinstall note\n", encoding="utf-8")
    run(command)
    assert_installed_examples(repository, project, "agents")
    assert_installed_examples(repository, project, "claude")
    reinstall_backups = list(
        (project / ".agents/skills").glob(
            "engineering-working-contract.mivia-backup-*/user-note.md"
        )
    )
    assert len(reinstall_backups) == 1
    assert reinstall_backups[0].read_text(encoding="utf-8") == "Keep this reinstall note\n"
    assert not reinstall_note.exists()

    registry = project / ".agents/skills/.mivia-agent-skills.json"
    valid_registry = registry.read_text(encoding="utf-8")
    protected_outside_skill = project / ".agents/forged-outside-skill"
    protected_outside_skill.mkdir()
    (protected_outside_skill / ".mivia-managed").write_text(
        "MiviaLabs/mivia-agent-skills\n", encoding="utf-8"
    )
    unmarked_skill = project / ".claude/skills/user-owned-skill"
    unmarked_skill.mkdir()
    (unmarked_skill / "SKILL.md").write_text("user-owned\n", encoding="utf-8")
    existing_backup = project / ".agents/skills/existing.mivia-backup-000000"
    existing_backup.write_text("keep\n", encoding="utf-8")
    unrelated = project / "unrelated-project-file.txt"
    unrelated.write_text("keep\n", encoding="utf-8")

    for unsafe_name in (
        "/tmp/forged-skill",
        "../forged-outside-skill",
        "nested/skill",
        "nested\\skill",
        None,
    ):
        registry.write_text(
            json.dumps(
                {
                    "source": "MiviaLabs/mivia-agent-skills",
                    "skills": [unsafe_name],
                }
            ),
            encoding="utf-8",
        )
        failed_uninstall = run(command + ["--uninstall"], check=False)
        assert failed_uninstall.returncode == 1
        assert "Installation failed:" in failed_uninstall.stderr
        assert "unsafe skill name" in failed_uninstall.stderr
        assert protected_outside_skill.exists()
        assert "BEGIN MIVIA" in codex_file.read_text(encoding="utf-8")
        assert "BEGIN MIVIA" in claude_file.read_text(encoding="utf-8")

    uninstall_note = project / ".claude/skills/verify-code-change/user-note.md"
    uninstall_note.write_text("Keep this uninstall note\n", encoding="utf-8")
    registry.write_text(valid_registry, encoding="utf-8")
    run(command + ["--uninstall"])
    assert "BEGIN MIVIA" not in codex_file.read_text(encoding="utf-8")
    assert "BEGIN MIVIA" not in claude_file.read_text(encoding="utf-8")
    assert "Keep this." in codex_file.read_text(encoding="utf-8")
    assert "Keep this." in claude_file.read_text(encoding="utf-8")
    assert not (project / ".agents/skills/.mivia-agent-skills.json").exists()
    assert not (project / ".agents/skills/engineering-working-contract").exists()
    assert not (project / ".claude/skills/verify-code-change").exists()
    assert not (project / ".agents/skills/deep-bug-audit").exists()
    assert not (project / ".claude/skills/deep-bug-audit").exists()
    assert protected_outside_skill.exists()
    assert unmarked_skill.exists()
    assert existing_backup.read_text(encoding="utf-8") == "keep\n"
    assert unrelated.read_text(encoding="utf-8") == "keep\n"
    for relative in example_files(repository):
        assert not (project / ".agents/skills" / relative).exists()
        assert not (project / ".claude/skills" / relative).exists()
    uninstall_backups = list(
        (project / ".claude/skills").glob("verify-code-change.mivia-backup-*/user-note.md")
    )
    assert len(uninstall_backups) == 1
    assert uninstall_backups[0].read_text(encoding="utf-8") == "Keep this uninstall note\n"


def test_packages(repository: Path, temporary: Path) -> None:
    output = temporary / "dist"
    run(
        [
            sys.executable,
            str(repository / "scripts/package_claude_skills.py"),
            "--output",
            str(output),
        ]
    )

    expected = {path.name for path in (repository / "skills").iterdir() if path.is_dir()}
    archives = {path.stem: path for path in output.glob("*.zip")}
    assert set(archives) == expected

    for name, archive_path in archives.items():
        with zipfile.ZipFile(archive_path) as archive:
            entries = set(archive.namelist())
        assert f"{name}/skill.md" in entries
        assert all(entry.startswith(f"{name}/") for entry in entries)
        assert not any("evaluations/" in entry for entry in entries)
        assert not any("agents/" in entry for entry in entries)
        source_examples = {
            relative.split("/", 1)[1]: content
            for relative, content in example_files(repository).items()
            if relative.startswith(f"{name}/")
        }
        for relative, content in source_examples.items():
            archive_name = f"{name}/{relative}"
            assert archive_name in entries
            with zipfile.ZipFile(archive_path) as archive:
                assert archive.read(archive_name) == content
        if name == "deep-bug-audit":
            assert f"{name}/references/bug-taxonomy.md" in entries
            assert f"{name}/scripts/audit_efficiency_score.py" in entries


def main() -> int:
    repository = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory() as temp_dir:
        temporary = Path(temp_dir)
        test_both_transaction_rollback(repository, temporary)
        test_both_uninstall_transaction_rollback(repository, temporary)
        test_installer(repository, temporary)
        test_packages(repository, temporary)
    print("Distribution tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
