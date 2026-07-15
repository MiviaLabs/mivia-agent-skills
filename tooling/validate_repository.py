#!/usr/bin/env python3
"""Validate repository structure and portable skill packaging."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

TEXT_SUFFIXES = {
    ".md",
    ".mmd",
    ".json",
    ".yaml",
    ".yml",
    ".py",
    ".sh",
    ".ps1",
    ".toml",
}
IGNORED_PARTS = {".git", ".venv", "dist", "__pycache__"}
PROHIBITED_PHRASES = (
    "dev" + " branch",
    "`dev`" + " branch",
    "early" + " development",
    "work is currently" + " maintained on",
)


def error(errors: list[str], message: str) -> None:
    errors.append(message)


def read_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    result: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip()
    return result


def strip_frontmatter(text: str) -> str:
    if not text.startswith("---\n"):
        return text
    end = text.find("\n---\n", 4)
    if end == -1:
        return text
    return text[end + 5 :].lstrip()


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors: list[str] = []

    for path in root.rglob("*"):
        if not path.is_file() or any(part in IGNORED_PARTS for part in path.parts):
            continue
        if path.suffix not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8")
        if chr(0x2014) in text:
            error(errors, f"Em dash found: {path.relative_to(root)}")
        lowered = text.lower()
        for phrase in PROHIBITED_PHRASES:
            if phrase in lowered:
                error(errors, f"Branch-status language found in {path.relative_to(root)}: {phrase}")
        if path.suffix == ".py":
            try:
                compile(text, str(path), "exec")
            except SyntaxError as exc:
                error(errors, f"Invalid Python in {path.relative_to(root)}: {exc}")
        if path.suffix == ".json":
            try:
                json.loads(text)
            except json.JSONDecodeError as exc:
                error(errors, f"Invalid JSON in {path.relative_to(root)}: {exc}")

    required = [
        ".codex-plugin/plugin.json",
        ".claude-plugin/plugin.json",
        ".agents/plugins/marketplace.json",
        ".claude-plugin/marketplace.json",
        "contracts/engineering-agent-working-contract.md",
        "bootstrap/manifest.json",
        "docs/installation.md",
        "tooling/test_distribution.py",
        "tooling/test_project_bootstrap.py",
        ".github/workflows/validate.yml",
        ".github/workflows/release-skills.yml",
    ]
    for relative in required:
        if not (root / relative).exists():
            error(errors, f"Required file missing: {relative}")

    skills_root = root / "skills"
    for skill in sorted(skills_root.iterdir()):
        if not skill.is_dir():
            continue
        skill_file = skill / "SKILL.md"
        if not skill_file.exists():
            error(errors, f"Skill missing SKILL.md: {skill.name}")
            continue

        metadata = read_frontmatter(skill_file)
        if not metadata.get("name"):
            error(errors, f"Skill missing name: {skill.name}")
        if not metadata.get("description"):
            error(errors, f"Skill missing description: {skill.name}")
        elif len(metadata["description"]) > 1024:
            error(errors, f"Skill description exceeds 1024 characters: {skill.name}")
        if metadata.get("name") != skill.name:
            error(errors, f"Skill folder and name differ: {skill.name}")

        evaluations = skill / "evaluations"
        if not evaluations.exists():
            error(errors, f"Skill missing evaluations: {skill.name}")
            continue

        trigger_values = set()
        for case in evaluations.glob("*.json"):
            try:
                data = json.loads(case.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            if "should_trigger" not in data:
                error(errors, f"Evaluation missing should_trigger: {case.relative_to(root)}")
            else:
                trigger_values.add(data["should_trigger"])

        if True not in trigger_values:
            error(errors, f"Skill missing positive activation evaluation: {skill.name}")
        if False not in trigger_values:
            error(errors, f"Skill missing negative activation evaluation: {skill.name}")

    contract = (root / "contracts/engineering-agent-working-contract.md").read_text(
        encoding="utf-8"
    ).strip()
    contract_skill = (
        root / "skills/engineering-working-contract/SKILL.md"
    ).read_text(encoding="utf-8")
    if strip_frontmatter(contract_skill).strip() != contract:
        error(errors, "Canonical contract and installable contract skill are not synchronized")

    article = root / "articles/engineering-working-contracts/README.md"
    if not article.exists():
        error(errors, "Primary article is missing")

    for markdown in root.rglob("*.md"):
        if any(part in IGNORED_PARTS for part in markdown.parts):
            continue
        text = markdown.read_text(encoding="utf-8")
        if text.count("```mermaid") > text.count("```"):
            error(errors, f"Unclosed Mermaid block: {markdown.relative_to(root)}")
        markdown_links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)
        for link in markdown_links:
            if "://" in link or link.startswith("#") or link.startswith("mailto:"):
                continue
            target = (markdown.parent / link.split("#", 1)[0]).resolve()
            if not target.exists():
                error(errors, f"Broken relative link in {markdown.relative_to(root)}: {link}")

    codex_manifest = json.loads((root / ".codex-plugin/plugin.json").read_text())
    claude_manifest = json.loads((root / ".claude-plugin/plugin.json").read_text())
    codex_marketplace = json.loads((root / ".agents/plugins/marketplace.json").read_text())
    claude_marketplace = json.loads((root / ".claude-plugin/marketplace.json").read_text())
    expected_name = "mivia-agentic-engineering"
    bootstrap_manifest = json.loads((root / "bootstrap/manifest.json").read_text())
    if bootstrap_manifest.get("schema") != 1:
        error(errors, "Bootstrap manifest schema is unsupported")
    if bootstrap_manifest.get("version") != codex_manifest.get("version"):
        error(errors, "Bootstrap manifest version does not match plugin version")
    if bootstrap_manifest.get("references") != [
        "contracts/engineering-agent-working-contract.md",
        "doctrines/evidence-before-claims.md",
        "doctrines/verification-is-part-of-delivery.md",
    ]:
        error(errors, "Bootstrap reference allowlist is not canonical")
    for relative in bootstrap_manifest.get("references", []):
        if not (root / relative).is_file():
            error(errors, f"Bootstrap reference is missing: {relative}")
    if codex_manifest.get("name") != expected_name or claude_manifest.get("name") != expected_name:
        error(errors, "Codex and Claude plugin names are not synchronized")
    if codex_marketplace.get("plugins", [{}])[0].get("name") != expected_name:
        error(errors, "Codex marketplace plugin name does not match the manifest")
    if claude_marketplace.get("plugins", [{}])[0].get("name") != expected_name:
        error(errors, "Claude marketplace plugin name does not match the manifest")
    if "version" in claude_marketplace.get("plugins", [{}])[0]:
        error(errors, "Claude marketplace must not duplicate the plugin manifest version")

    if errors:
        for message in errors:
            print(f"ERROR: {message}")
        print(f"{len(errors)} validation error(s)")
        return 1

    print("Repository validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
