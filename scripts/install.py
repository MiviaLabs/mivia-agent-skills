#!/usr/bin/env python3
"""Install or remove Mivia engineering instructions and skills."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PureWindowsPath

BEGIN = "<!-- BEGIN MIVIA AGENTIC ENGINEERING CONTRACT -->"
END = "<!-- END MIVIA AGENTIC ENGINEERING CONTRACT -->"
RUNTIME_DIRS = ("references", "scripts", "assets")
SKILL_MARKER = ".mivia-managed"
REGISTRY = ".mivia-agent-skills.json"
MANAGED_ROOT = ".mivia-agent-skills"
MANAGED_MANIFEST = "manifest.json"
SOURCE_ID = "MiviaLabs/mivia-agent-skills"
BOOTSTRAP_MANIFEST = "bootstrap/manifest.json"
REFERENCE_FILES = (
    "contracts/engineering-agent-working-contract.md",
    "doctrines/evidence-before-claims.md",
    "doctrines/verification-is-part-of-delivery.md",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install the engineering working contract and skills."
    )
    parser.add_argument("--scope", choices=("global", "project"), required=True)
    parser.add_argument("--target", choices=("codex", "claude", "both"), default="both")
    parser.add_argument("--project", type=Path)
    parser.add_argument("--uninstall", action="store_true")
    return parser.parse_args()


def timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def backup_file(path: Path, backup_log: list[Path] | None = None) -> Path | None:
    if not path.exists() or not path.read_text(encoding="utf-8").strip():
        return None
    candidate = path.with_name(f"{path.name}.mivia-backup-{timestamp()}")
    if backup_log is not None:
        backup_log.append(candidate)
    shutil.copy2(path, candidate)
    return candidate


def backup_directory(path: Path, backup_log: list[Path] | None = None) -> Path:
    candidate = path.with_name(f"{path.name}.mivia-backup-{timestamp()}")
    if backup_log is not None:
        backup_log.append(candidate)
    shutil.copytree(path, candidate)
    return candidate


def managed_block(contract: str, reference_root: str) -> str:
    return (
        f"{BEGIN}\n"
        "This repository has the Mivia Agentic Engineering runtime installed.\n\n"
        "Apply the complete standing contract below. The canonical copy and\n"
        f"supporting doctrines are also available under `{reference_root}`.\n\n"
        f"{contract.rstrip()}\n"
        f"{END}"
    )


def update_managed_file(
    path: Path,
    contract: str,
    reference_root: str,
    backup_log: list[Path] | None = None,
) -> Path | None:
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    block = managed_block(contract, reference_root)

    if BEGIN in existing or END in existing:
        if BEGIN not in existing or END not in existing:
            raise RuntimeError(f"Malformed managed block in {path}")
        start = existing.index(BEGIN)
        finish = existing.index(END, start) + len(END)
        updated = existing[:start].rstrip() + "\n\n" + block + existing[finish:]
        normalized = updated.strip() + "\n"
        if existing != normalized:
            backup_file(path, backup_log)
            path.write_text(normalized, encoding="utf-8")
        return None

    created_backup = backup_file(path, backup_log)
    prefix = existing.rstrip()
    updated = f"{prefix}\n\n{block}\n" if prefix else f"{block}\n"
    path.write_text(updated, encoding="utf-8")
    return created_backup


def remove_managed_block(
    path: Path, backup_log: list[Path] | None = None
) -> None:
    if not path.exists():
        return
    existing = path.read_text(encoding="utf-8")
    if BEGIN not in existing and END not in existing:
        return
    if BEGIN not in existing or END not in existing:
        raise RuntimeError(f"Malformed managed block in {path}")
    start = existing.index(BEGIN)
    finish = existing.index(END, start) + len(END)
    updated = (existing[:start].rstrip() + "\n\n" + existing[finish:].lstrip()).strip()
    if updated:
        backup_file(path, backup_log)
        path.write_text(updated + "\n", encoding="utf-8")
    else:
        backup_file(path, backup_log)
        path.write_text("", encoding="utf-8")


def read_registry(destination_root: Path) -> set[str]:
    path = destination_root / REGISTRY
    if not path.exists():
        return set()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise RuntimeError(f"Invalid installation registry at {path}: {exc}") from exc
    if (
        not isinstance(data, dict)
        or data.get("source") != SOURCE_ID
        or not isinstance(data.get("skills"), list)
    ):
        raise RuntimeError(f"Unrecognized installation registry at {path}")

    skills = set()
    for name in data["skills"]:
        if not is_safe_skill_name(name):
            raise RuntimeError(f"Invalid installation registry at {path}: unsafe skill name")
        skills.add(name)
    return skills


def is_safe_skill_name(name: object) -> bool:
    if not isinstance(name, str) or not name or name in {".", ".."}:
        return False
    if "/" in name or "\\" in name:
        return False

    native_path = Path(name)
    windows_path = PureWindowsPath(name)
    return (
        not native_path.is_absolute()
        and native_path.parent == Path(".")
        and native_path.name == name
        and not windows_path.is_absolute()
        and not windows_path.drive
        and windows_path.parent == PureWindowsPath(".")
        and windows_path.name == name
    )


def write_registry(destination_root: Path, skills: set[str]) -> None:
    destination_root.mkdir(parents=True, exist_ok=True)
    payload = {"source": SOURCE_ID, "skills": sorted(skills)}
    (destination_root / REGISTRY).write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )


def sha256_file(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(65536):
            digest.update(chunk)
    return digest.hexdigest()


def bootstrap_spec(repository: Path) -> dict[str, object]:
    path = repository / BOOTSTRAP_MANIFEST
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Invalid bootstrap manifest at {path}: {exc}") from exc
    if (
        not isinstance(data, dict)
        or data.get("schema") != 1
        or not isinstance(data.get("version"), str)
    ):
        raise RuntimeError(f"Unsupported bootstrap manifest at {path}")
    references = data.get("references")
    if references != list(REFERENCE_FILES):
        raise RuntimeError(f"Bootstrap reference allowlist does not match {path}")
    for relative in references:
        source = repository / relative
        if not source.is_file():
            raise RuntimeError(f"Bootstrap reference is missing: {relative}")
    return data


def read_managed_manifest(root: Path) -> dict[str, object] | None:
    path = root / MANAGED_MANIFEST
    if not path.exists():
        return None
    if path.is_symlink():
        raise RuntimeError(f"Refusing to read symlinked managed manifest at {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Invalid managed manifest at {path}: {exc}") from exc
    if not isinstance(data, dict) or data.get("source") != SOURCE_ID:
        raise RuntimeError(f"Unrecognized managed manifest at {path}")
    if data.get("schema") != 1 or not isinstance(data.get("targets"), list):
        raise RuntimeError(f"Unsupported managed manifest at {path}")
    if any(target not in {"codex", "claude"} for target in data["targets"]):
        raise RuntimeError(f"Invalid target in managed manifest at {path}")
    return data


def install_references(
    repository: Path,
    destination: Path,
    version: str,
    targets: tuple[str, ...],
    skills_root: Path,
    backup_log: list[Path] | None = None,
) -> None:
    if destination.exists() and read_managed_manifest(destination) is None:
        raise RuntimeError(f"Unrecognized managed root at {destination}")
    destination.mkdir(parents=True, exist_ok=True)
    references = destination / "references"
    manifest_path = destination / MANAGED_MANIFEST
    if manifest_path.is_symlink() or references.is_symlink():
        raise RuntimeError(f"Refusing to operate through symlinked managed content at {destination}")
    if references.exists() and not references.is_dir():
        raise RuntimeError(f"Managed reference path is not a directory: {references}")
    references.mkdir(parents=True, exist_ok=True)
    digests: dict[str, str] = {}
    for relative in REFERENCE_FILES:
        source = repository / relative
        if relative.startswith("contracts/"):
            target = references / "engineering-agent-working-contract.md"
            key = "engineering-agent-working-contract.md"
        else:
            target = references / "doctrines" / Path(relative).name
            key = f"doctrines/{Path(relative).name}"
        reject_symlink_path(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.is_symlink():
            raise RuntimeError(f"Refusing to overwrite symlinked managed reference at {target}")
        if not target.exists() or not files_match(source, target):
            if target.exists():
                backup_file(target, backup_log)
            shutil.copy2(source, target)
        digests[key] = sha256_file(source)
    skill_digests = {
        source.name: sha256_file(source / "SKILL.md")
        for source in sorted(skills_root.iterdir())
        if source.is_dir() and (source / "SKILL.md").is_file()
    }
    manifest = {
        "schema": 1,
        "source": SOURCE_ID,
        "version": version,
        "targets": sorted(set(targets)),
        "references": digests,
        "skills": skill_digests,
    }
    (destination / MANAGED_MANIFEST).write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


def update_reference_targets(destination: Path, targets: tuple[str, ...]) -> None:
    manifest = read_managed_manifest(destination)
    if manifest is None:
        return
    manifest["targets"] = sorted(set(targets))
    (destination / MANAGED_MANIFEST).write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


def remove_references(destination: Path, backup_log: list[Path] | None = None) -> None:
    if not destination.exists():
        return
    manifest = read_managed_manifest(destination)
    if manifest is None:
        raise RuntimeError(f"Cannot remove untracked managed root: {destination}")
    if backup_log is not None:
        backup_directory(destination, backup_log)
    shutil.rmtree(destination)


def is_managed_skill(path: Path) -> bool:
    marker = path / SKILL_MARKER
    return marker.exists() and marker.read_text(encoding="utf-8").strip() == SOURCE_ID


def files_match(source: Path, destination: Path) -> bool:
    if not source.is_file() or not destination.is_file():
        return False
    if source.stat().st_size != destination.stat().st_size:
        return False

    with source.open("rb") as source_file, destination.open("rb") as destination_file:
        while source_chunk := source_file.read(65536):
            if source_chunk != destination_file.read(65536):
                return False
    return True


def directories_match(source: Path, destination: Path) -> bool:
    if not source.is_dir() or not destination.is_dir():
        return False

    source_entries = {path.name: path for path in source.iterdir()}
    destination_entries = {path.name: path for path in destination.iterdir()}
    if source_entries.keys() != destination_entries.keys():
        return False

    for name, source_entry in source_entries.items():
        destination_entry = destination_entries[name]
        if source_entry.is_dir():
            if not directories_match(source_entry, destination_entry):
                return False
        elif not source_entry.is_file() or not destination_entry.is_file():
            return False
        elif not files_match(source_entry, destination_entry):
            return False
    return True


def managed_skill_matches_source(source: Path, destination: Path, target: str) -> bool:
    expected_entries = {"SKILL.md", SKILL_MARKER}
    expected_entries.update(
        directory for directory in RUNTIME_DIRS if (source / directory).exists()
    )
    if target == "codex" and (source / "agents").exists():
        expected_entries.add("agents")

    if (
        not destination.is_dir()
        or {path.name for path in destination.iterdir()} != expected_entries
    ):
        return False
    if not is_managed_skill(destination):
        return False
    if not files_match(source / "SKILL.md", destination / "SKILL.md"):
        return False

    for directory in expected_entries - {"SKILL.md", SKILL_MARKER}:
        if not directories_match(source / directory, destination / directory):
            return False
    return True


def resolved_direct_child(destination_root: Path, name: str) -> Path | None:
    candidate = destination_root / name
    if not candidate.exists():
        return None

    resolved_root = destination_root.resolve(strict=True)
    resolved_candidate = candidate.resolve(strict=True)
    if resolved_candidate.parent != resolved_root:
        raise RuntimeError(
            f"Refusing to remove skill outside installation root: {candidate}"
        )
    return candidate


def copy_skill(
    source: Path,
    destination: Path,
    target: str,
    backup_log: list[Path] | None = None,
) -> Path | None:
    created_backup = None
    if destination.is_symlink():
        raise RuntimeError(f"Refusing to operate through symlinked skill at {destination}")
    if destination.exists():
        if is_managed_skill(destination):
            if not managed_skill_matches_source(source, destination, target):
                created_backup = backup_directory(destination, backup_log)
            shutil.rmtree(destination)
        else:
            raise RuntimeError(
                f"Unmarked skill collision at {destination}; remove it or choose another name"
            )

    destination.mkdir(parents=True)
    shutil.copy2(source / "SKILL.md", destination / "SKILL.md")

    for directory in RUNTIME_DIRS:
        candidate = source / directory
        if candidate.exists():
            shutil.copytree(candidate, destination / directory)

    if target == "codex":
        metadata = source / "agents"
        if metadata.exists():
            shutil.copytree(metadata, destination / "agents")

    (destination / SKILL_MARKER).write_text(SOURCE_ID + "\n", encoding="utf-8")
    return created_backup


def install_skills(
    source_root: Path,
    destination_root: Path,
    target: str,
    backup_log: list[Path] | None = None,
) -> list[Path]:
    destination_root.mkdir(parents=True, exist_ok=True)
    previous = read_registry(destination_root)
    current = {
        source.name
        for source in source_root.iterdir()
        if source.is_dir() and (source / "SKILL.md").exists()
    }
    backups = []

    for stale_name in sorted(previous - current):
        stale = resolved_direct_child(destination_root, stale_name)
        if stale is not None and is_managed_skill(stale):
            created_backup = backup_directory(stale, backup_log)
            backups.append(created_backup)
            shutil.rmtree(stale)

    for source in sorted(source_root.iterdir()):
        if source.is_dir() and (source / "SKILL.md").exists():
            created_backup = copy_skill(
                source, destination_root / source.name, target, backup_log
            )
            if created_backup:
                backups.append(created_backup)

    write_registry(destination_root, current)
    return backups


def remove_skills(
    destination_root: Path, backup_log: list[Path] | None = None
) -> list[Path]:
    if not destination_root.exists():
        return []
    installed = read_registry(destination_root)
    backups = []
    for name in sorted(installed):
        destination = resolved_direct_child(destination_root, name)
        if destination is not None and is_managed_skill(destination):
            created_backup = backup_directory(destination, backup_log)
            backups.append(created_backup)
            shutil.rmtree(destination)
    registry = destination_root / REGISTRY
    if registry.exists():
        registry.unlink()
    return backups


@dataclass
class PathSnapshot:
    path: Path
    existed: bool
    kind: str | None
    staged: Path | None


@dataclass
class TargetSnapshot:
    instruction: PathSnapshot
    registry: PathSnapshot
    skills: list[PathSnapshot]
    cleanup_directories: tuple[Path, ...]


def snapshot_path(path: Path, staged: Path) -> PathSnapshot:
    reject_symlink_path(path)
    if not path.exists():
        return PathSnapshot(path, False, None, None)
    if path.is_dir():
        staged.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(path, staged)
        return PathSnapshot(path, True, "directory", staged)
    if path.is_file():
        staged.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, staged)
        return PathSnapshot(path, True, "file", staged)
    raise RuntimeError(f"Cannot snapshot unsupported path type: {path}")


def reject_symlink_path(path: Path) -> None:
    current = path
    while True:
        if current.is_symlink():
            raise RuntimeError(f"Refusing to operate through symlink path: {path}")
        if current.parent == current:
            return
        current = current.parent


def absent_directory_ancestors(path: Path) -> list[Path]:
    missing = []
    current = path
    while not current.exists():
        missing.append(current)
        current = current.parent
    return missing


def source_skill_names(source_root: Path) -> set[str]:
    return {
        source.name
        for source in source_root.iterdir()
        if source.is_dir() and (source / "SKILL.md").exists()
    }


def snapshot_target(
    instruction_file: Path,
    skill_directory: Path,
    source_root: Path,
    uninstall: bool,
    staging_root: Path,
) -> TargetSnapshot:
    reject_symlink_path(instruction_file)
    reject_symlink_path(skill_directory)
    installed = read_registry(skill_directory)
    names = installed if uninstall else installed | source_skill_names(source_root)
    instruction = snapshot_path(instruction_file, staging_root / "instruction")
    registry = snapshot_path(
        skill_directory / REGISTRY, staging_root / "registry"
    )
    skills = [
        snapshot_path(
            skill_directory / name,
            staging_root / "skills" / name,
        )
        for name in sorted(names)
    ]
    cleanup_directories = tuple(
        dict.fromkeys(
            absent_directory_ancestors(instruction_file.parent)
            + absent_directory_ancestors(skill_directory)
        )
    )
    return TargetSnapshot(instruction, registry, skills, cleanup_directories)


def remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def restore_path(snapshot: PathSnapshot) -> None:
    if snapshot.path.exists() or snapshot.path.is_symlink():
        remove_path(snapshot.path)
    if not snapshot.existed:
        return
    snapshot.path.parent.mkdir(parents=True, exist_ok=True)
    if snapshot.kind == "directory":
        shutil.copytree(snapshot.staged, snapshot.path)
    elif snapshot.kind == "file":
        shutil.copy2(snapshot.staged, snapshot.path)
    else:
        raise RuntimeError(f"Cannot restore unsupported snapshot: {snapshot.path}")


class InstallationTransaction:
    def __init__(self) -> None:
        self.snapshots: list[TargetSnapshot] = []
        self.shared_snapshot: PathSnapshot | None = None
        self.shared_cleanup_directories: tuple[Path, ...] = ()
        self.created_backups: list[Path] = []

    def prepare(
        self,
        selected: dict[str, tuple[Path, Path]],
        targets: tuple[str, ...],
        source_root: Path,
        uninstall: bool,
        staging_root: Path,
        managed_root: Path,
    ) -> None:
        reject_symlink_path(managed_root)
        self.snapshots = [
            snapshot_target(
                selected[target][0],
                selected[target][1],
                source_root,
                uninstall,
                staging_root / target,
            )
            for target in targets
        ]
        self.shared_snapshot = snapshot_path(
            managed_root, staging_root / "shared"
        )
        self.shared_cleanup_directories = tuple(absent_directory_ancestors(managed_root))

    def rollback(self) -> None:
        errors = []
        for backup in reversed(self.created_backups):
            try:
                if backup.exists() or backup.is_symlink():
                    remove_path(backup)
            except OSError as exc:
                errors.append(f"remove backup {backup}: {exc}")

        for snapshot in reversed(self.snapshots):
            for path_snapshot in (
                snapshot.registry,
                *reversed(snapshot.skills),
                snapshot.instruction,
            ):
                try:
                    restore_path(path_snapshot)
                except OSError as exc:
                    errors.append(f"restore {path_snapshot.path}: {exc}")
            for directory in sorted(
                snapshot.cleanup_directories, key=lambda path: len(path.parts), reverse=True
            ):
                try:
                    if directory.is_dir() and not any(directory.iterdir()):
                        directory.rmdir()
                except OSError as exc:
                    errors.append(f"remove created directory {directory}: {exc}")

        if self.shared_snapshot is not None:
            try:
                restore_path(self.shared_snapshot)
            except OSError as exc:
                errors.append(f"restore {self.shared_snapshot.path}: {exc}")
            for directory in sorted(
                self.shared_cleanup_directories,
                key=lambda path: len(path.parts),
                reverse=True,
            ):
                try:
                    if directory.is_dir() and not any(directory.iterdir()):
                        directory.rmdir()
                except OSError as exc:
                    errors.append(f"remove created directory {directory}: {exc}")

        if errors:
            raise RuntimeError("; ".join(errors))


def locations(args: argparse.Namespace) -> dict[str, tuple[Path, Path]]:
    home = Path.home()

    if args.scope == "project":
        if args.project is None:
            raise ValueError("--project is required when --scope project is used")
        project = args.project.expanduser().resolve()
        if not project.exists() or not project.is_dir():
            raise ValueError(f"Project directory does not exist: {project}")
        return {
            "codex": (project / "AGENTS.md", project / ".agents" / "skills"),
            "claude": (project / "CLAUDE.md", project / ".claude" / "skills"),
        }

    codex_home = Path(os.environ.get("CODEX_HOME", home / ".codex")).expanduser()
    return {
        "codex": (codex_home / "AGENTS.md", home / ".agents" / "skills"),
        "claude": (home / ".claude" / "CLAUDE.md", home / ".claude" / "skills"),
    }


def managed_root(args: argparse.Namespace) -> Path:
    if args.scope == "project":
        if args.project is None:
            raise ValueError("--project is required when --scope project is used")
        return args.project.expanduser().resolve() / MANAGED_ROOT
    return Path.home() / MANAGED_ROOT


def main() -> int:
    args = parse_args()
    repository = Path(__file__).resolve().parents[1]
    contract_path = repository / "contracts" / "engineering-agent-working-contract.md"
    skills_root = repository / "skills"

    if not contract_path.exists() or not skills_root.exists():
        print("Run this script from a complete repository checkout.", file=sys.stderr)
        return 2

    try:
        bootstrap = bootstrap_spec(repository)
    except RuntimeError as exc:
        print(f"Installation failed: {exc}", file=sys.stderr)
        return 1

    contract = contract_path.read_text(encoding="utf-8")
    targets = ("codex", "claude") if args.target == "both" else (args.target,)
    selected = locations(args)
    shared_root = managed_root(args)
    try:
        reject_symlink_path(shared_root)
        existing_manifest = (
            read_managed_manifest(shared_root) if shared_root.exists() else None
        )
    except RuntimeError as exc:
        print(f"Installation failed: {exc}", file=sys.stderr)
        return 1
    if shared_root.exists() and existing_manifest is None and not args.uninstall:
        print(f"Installation failed: Unrecognized managed root at {shared_root}", file=sys.stderr)
        return 1

    if args.uninstall:
        installed_targets = set(existing_manifest.get("targets", [])) if existing_manifest else set()
        remaining_targets = tuple(sorted(installed_targets - set(targets)))
    else:
        installed_targets = set(existing_manifest.get("targets", [])) if existing_manifest else set()
        remaining_targets = tuple(sorted(installed_targets | set(targets)))

    reference_root = (
        "`.mivia-agent-skills/references`"
        if args.scope == "project"
        else "`~/.mivia-agent-skills/references`"
    )

    transaction = InstallationTransaction()
    output: list[str] = []
    staging = tempfile.TemporaryDirectory(prefix="mivia-install-")
    try:
        transaction.prepare(
            selected,
            targets,
            skills_root,
            args.uninstall,
            Path(staging.name),
            shared_root,
        )
        if args.uninstall:
            if shared_root.exists() and existing_manifest is not None:
                if remaining_targets:
                    update_reference_targets(shared_root, remaining_targets)
                else:
                    remove_references(shared_root, transaction.created_backups)
        else:
            install_references(
                repository,
                shared_root,
                str(bootstrap["version"]),
                remaining_targets,
                skills_root,
                transaction.created_backups,
            )
        for target in targets:
            instruction_file, skill_directory = selected[target]
            backup_start = len(transaction.created_backups)
            if args.uninstall:
                remove_skills(skill_directory, transaction.created_backups)
                remove_managed_block(instruction_file, transaction.created_backups)
                output.append(
                    f"Removed {target} installation from {instruction_file.parent}"
                )
            else:
                update_managed_file(
                    instruction_file,
                    contract,
                    reference_root,
                    transaction.created_backups,
                )
                install_skills(
                    skills_root,
                    skill_directory,
                    target,
                    transaction.created_backups,
                )
                output.append(f"Installed {target} contract: {instruction_file}")
                output.append(f"Installed {target} skills: {skill_directory}")
            for backup in transaction.created_backups[backup_start:]:
                if backup.parent == skill_directory:
                    label = "Skill"
                elif backup.parent == shared_root.parent:
                    label = "Reference"
                else:
                    label = "Instruction"
                output.append(f"{label} backup created: {backup}")
    except (OSError, RuntimeError, ValueError) as exc:
        if transaction.snapshots:
            try:
                transaction.rollback()
            except RuntimeError as rollback_exc:
                print(
                    f"Installation failed: {exc}; rollback failed: {rollback_exc}",
                    file=sys.stderr,
                )
                staging.cleanup()
                return 1
        staging.cleanup()
        print(f"Installation failed: {exc}", file=sys.stderr)
        return 1
    staging.cleanup()

    for line in output:
        print(line)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
