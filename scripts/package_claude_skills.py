#!/usr/bin/env python3
"""Package repository skills for Claude Desktop and Cowork upload."""

from __future__ import annotations

import argparse
import shutil
import tempfile
import zipfile
from pathlib import Path

EXCLUDED_ENTRIES = {"agents", "evaluations"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("dist"))
    return parser.parse_args()


def package_skill(skill: Path, output: Path) -> Path:
    output.mkdir(parents=True, exist_ok=True)
    archive_path = output / f"{skill.name}.zip"

    with tempfile.TemporaryDirectory() as temp_dir:
        staging_root = Path(temp_dir) / skill.name
        staging_root.mkdir()

        shutil.copy2(skill / "SKILL.md", staging_root / "skill.md")
        for source in skill.iterdir():
            if source.name == "SKILL.md" or source.name in EXCLUDED_ENTRIES:
                continue
            destination = staging_root / source.name
            if source.is_dir():
                shutil.copytree(source, destination)
            else:
                shutil.copy2(source, destination)

        with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(staging_root.rglob("*")):
                if path.is_file():
                    archive.write(
                        path,
                        path.relative_to(staging_root.parent).as_posix(),
                    )

    return archive_path


def main() -> int:
    args = parse_args()
    repository = Path(__file__).resolve().parents[1]
    skills_root = repository / "skills"

    packages = []
    for skill in sorted(skills_root.iterdir()):
        if skill.is_dir() and (skill / "SKILL.md").exists():
            packages.append(package_skill(skill, args.output.resolve()))

    for package in packages:
        print(package)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
