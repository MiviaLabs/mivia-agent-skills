#!/usr/bin/env python3
"""Exercise the integrated project bootstrap contract in isolated repositories."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


def run(command: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, text=True, capture_output=True)
    if check and result.returncode != 0:
        raise RuntimeError(
            f"Command failed: {' '.join(command)}\n{result.stdout}\n{result.stderr}"
        )
    return result


def installer(repository: Path, project: Path, target: str, uninstall: bool = False) -> list[str]:
    command = [
        sys.executable,
        str(repository / "scripts/install.py"),
        "--scope",
        "project",
        "--target",
        target,
        "--project",
        str(project),
    ]
    if uninstall:
        command.append("--uninstall")
    return command


def test_integrated_bootstrap(repository: Path, temporary: Path) -> None:
    project = temporary / "project"
    project.mkdir()
    (project / "AGENTS.md").write_text("# Project rules\n", encoding="utf-8")
    (project / "CLAUDE.md").write_text("# Claude rules\n", encoding="utf-8")

    run(installer(repository, project, "both"))
    root = project / ".mivia-agent-skills"
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["targets"] == ["claude", "codex"]
    assert set(manifest["skills"]) == {
        "deep-bug-audit",
        "engineering-working-contract",
        "verify-code-change",
    }
    assert (root / "references/engineering-agent-working-contract.md").exists()
    assert (root / "references/doctrines/evidence-before-claims.md").exists()
    assert (project / ".agents/skills/deep-bug-audit/references/bug-taxonomy.md").exists()
    assert (project / ".agents/skills/deep-bug-audit/scripts/audit_efficiency_score.py").exists()
    assert (project / ".claude/skills/deep-bug-audit/references/bug-taxonomy.md").exists()
    assert (project / ".claude/skills/deep-bug-audit/scripts/audit_efficiency_score.py").exists()
    assert "mivia-agent-skills/references" in (project / "AGENTS.md").read_text(
        encoding="utf-8"
    )
    assert "mivia-agent-skills/references" in (project / "CLAUDE.md").read_text(
        encoding="utf-8"
    )
    assert not (project / "articles").exists()
    assert not (project / "docs").exists()
    assert not (project / "scripts").exists()

    backups_before_repeat = sorted(project.rglob("*.mivia-backup-*"))
    run(installer(repository, project, "both"))
    assert sorted(project.rglob("*.mivia-backup-*")) == backups_before_repeat

    run(installer(repository, project, "codex", uninstall=True))
    assert "BEGIN MIVIA" not in (project / "AGENTS.md").read_text(encoding="utf-8")
    assert "BEGIN MIVIA" in (project / "CLAUDE.md").read_text(encoding="utf-8")
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["targets"] == ["claude"]
    assert (project / ".claude/skills/verify-code-change").exists()
    assert (project / ".claude/skills/deep-bug-audit").exists()
    assert not (project / ".agents/skills/verify-code-change").exists()

    run(installer(repository, project, "claude", uninstall=True))
    assert not root.exists()
    assert (project / "AGENTS.md").exists()
    assert (project / "CLAUDE.md").exists()


def test_fail_closed_symlink_root(repository: Path, temporary: Path) -> None:
    project = temporary / "symlink-project"
    project.mkdir()
    outside = temporary / "outside"
    outside.mkdir()
    (outside / "manifest.json").write_text(
        json.dumps(
            {
                "schema": 1,
                "source": "MiviaLabs/mivia-agent-skills",
                "version": "0.1.0",
                "targets": ["codex", "claude"],
                "references": {},
                "skills": {},
            }
        ),
        encoding="utf-8",
    )
    outside_before = sorted(path.relative_to(outside) for path in outside.rglob("*"))
    (project / ".mivia-agent-skills").symlink_to(outside, target_is_directory=True)

    result = run(installer(repository, project, "both"), check=False)
    assert result.returncode == 1
    assert "symlink path" in result.stderr
    assert sorted(path.relative_to(outside) for path in outside.rglob("*")) == outside_before


def test_preserve_empty_instruction_file(repository: Path, temporary: Path) -> None:
    project = temporary / "empty-instruction-project"
    project.mkdir()
    instruction = project / "AGENTS.md"
    instruction.write_text("", encoding="utf-8")

    run(installer(repository, project, "codex"))
    run(installer(repository, project, "codex", uninstall=True))
    assert instruction.exists()
    assert instruction.read_text(encoding="utf-8") == ""


def main() -> int:
    repository = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory() as temp_dir:
        temporary = Path(temp_dir)
        test_integrated_bootstrap(repository, temporary)
        test_fail_closed_symlink_root(repository, temporary)
        test_preserve_empty_instruction_file(repository, temporary)
    print("Project bootstrap tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
