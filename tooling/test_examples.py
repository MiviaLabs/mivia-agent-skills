#!/usr/bin/env python3
"""Validate the curated skill usage examples and their navigation links."""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = {
    "engineering-working-contract": (
        "01-concurrency-fix.md",
        "02-production-containment.md",
    ),
    "verify-code-change": (
        "01-parser-regression-pass.md",
        "02-database-migration-partial.md",
    ),
    "agent-readiness-audit": (
        "01-bounded-action-readiness.md",
        "02-repository-readiness-gated.md",
    ),
    "agent-readiness-audit-go": (
        "01-repository-autonomy-readiness.md",
        "02-agent-runtime-readiness-gated.md",
    ),
    "mivia-image-generation": (
        "01-readme-banner.md",
        "02-image-capability-unavailable.md",
    ),
    "agent-readiness-audit-go": (
        "01-repository-autonomy-readiness.md",
        "02-agent-runtime-readiness-gated.md",
    ),
}
REQUIRED_SECTIONS = (
    "Use this when",
    "Request template",
    "Replace before running",
    "Required context",
    "What good looks like",
    "Illustrative handoff",
    "Verification checklist",
    "Failure or escalation signals",
)
LINK = re.compile(r"!?(?:\[[^\]]*\])\(([^)]+)\)")
FORBIDDEN_CLAIMS = (
    re.compile(r"\b(?:tests?|checks?|commands?)\s+(?:passed|succeeded)\b", re.I),
    re.compile(r"\bruntime evidence confirms\b", re.I),
    re.compile(
        r"\b(?:runtime verification|production verification|live verification|"
        r"command execution|image generation|artifact generation)\s+"
        r"(?:completed|succeeded|passed|confirmed|verified)(?:\s+successfully)?\b",
        re.I,
    ),
    re.compile(r"\bimage was created\b", re.I),
    re.compile(r"\bcreated the image\b", re.I),
)


def expected_paths() -> list[Path]:
    return [
        ROOT / "skills" / skill / "references" / "examples" / filename
        for skill, filenames in EXAMPLES.items()
        for filename in filenames
    ]


def markdown_links(text: str) -> list[str]:
    destinations = []
    for raw in LINK.findall(text):
        destination = raw[1:-1] if raw.startswith("<") and raw.endswith(">") else raw
        parsed = urlsplit(destination)
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        destinations.append(parsed.path)
    return destinations


def section_bodies(text: str) -> dict[str, str]:
    lines = text.splitlines()
    sections: dict[str, list[str]] = {heading: [] for heading in REQUIRED_SECTIONS}
    current: str | None = None
    for line in lines:
        if line.startswith("## "):
            heading = line[3:].strip()
            current = heading if heading in sections else None
            continue
        if current is not None:
            sections[current].append(line)
    return {heading: "\n".join(body).strip() for heading, body in sections.items()}


def test_expected_examples_exist() -> None:
    discovered = {
        path.relative_to(ROOT / "skills").as_posix()
        for skill in EXAMPLES
        for path in (ROOT / "skills" / skill / "references" / "examples").rglob("*")
        if path.is_file()
    }
    expected = {
        f"{skill}/references/examples/{filename}"
        for skill, filenames in EXAMPLES.items()
        for filename in filenames
    }
    assert discovered == expected
    assert all(path.is_file() and not path.is_symlink() for path in expected_paths())


def test_examples_have_required_sections() -> None:
    for path in expected_paths():
        text = path.read_text(encoding="utf-8")
        headings = [line[3:].strip() for line in text.splitlines() if line.startswith("## ")]
        assert headings == list(REQUIRED_SECTIONS), path
        assert text.splitlines()[0].startswith("# "), path
        assert sum(line.startswith("# ") for line in text.splitlines()) == 1, path
        bodies = section_bodies(text)
        assert all(bodies[heading] for heading in REQUIRED_SECTIONS), path
        outcomes = bodies["What good looks like"].splitlines()
        assert 1 <= sum(line.startswith("- ") for line in outcomes) <= 3, path


def test_examples_require_adaptation_and_label_handoffs() -> None:
    for path in expected_paths():
        text = path.read_text(encoding="utf-8")
        skill = path.parents[2]
        assert len(text.splitlines()) < len(
            (skill / "SKILL.md").read_text(encoding="utf-8").splitlines()
        ), path
        assert "Adapt this request" in text, path
        assert "{{" in text, path
        assert "Approval owner:" in section_bodies(text)["Required context"], path
        assert "illustrative" in text.lower(), path
        assert "not" in section_bodies(text)["Illustrative handoff"].lower(), path
        assert not any(pattern.search(text) for pattern in FORBIDDEN_CLAIMS), path


def test_sibling_examples_have_distinct_content() -> None:
    for skill, filenames in EXAMPLES.items():
        first, second = (
            (ROOT / "skills" / skill / "references" / "examples" / filename).read_text(
                encoding="utf-8"
            )
            for filename in filenames
        )
        assert first != second, skill
        assert first.split("## Request template", 1)[1] != second.split(
            "## Request template", 1
        )[1], skill


def test_example_pointers_and_index_links_resolve() -> None:
    index = ROOT / "docs/examples.md"
    index_text = index.read_text(encoding="utf-8")
    readme_text = (ROOT / "README.md").read_text(encoding="utf-8")
    installation_text = (ROOT / "docs/installation.md").read_text(encoding="utf-8")
    assert "docs/examples.md" in readme_text
    assert "examples.md" in installation_text

    for skill, filenames in EXAMPLES.items():
        skill_file = ROOT / "skills" / skill / "SKILL.md"
        skill_text = skill_file.read_text(encoding="utf-8")
        for filename in filenames:
            relative = f"references/examples/{filename}"
            assert any(
                line.strip() == f"- {relative}"
                or line.strip() == f"- `{relative}`"
                or line.strip()
                == f"- `skills/{skill}/{relative}`"
                or line.strip().endswith(f"]({relative})")
                for line in skill_text.splitlines()
            ), skill_file
            assert (skill_file.parent / relative).is_file(), relative
            index_link = f"../skills/{skill}/{relative}"
            assert index_link in index_text, index_link
            assert (index.parent / index_link).resolve().is_file()

    for link in markdown_links(index_text):
        target = (index.parent / link).resolve()
        assert target.is_relative_to(ROOT.resolve()), link
        assert target.exists(), link
    assert all((ROOT / link).resolve().exists() for link in markdown_links(readme_text))
    assert all((ROOT / "docs" / link).resolve().exists() for link in markdown_links(installation_text))


def test_example_links_stay_inside_owning_skill() -> None:
    for skill, filenames in EXAMPLES.items():
        skill_root = (ROOT / "skills" / skill / "references" / "examples").resolve()
        skill_file = ROOT / "skills" / skill / "SKILL.md"
        for link in markdown_links(skill_file.read_text(encoding="utf-8")):
            target = (skill_file.parent / link).resolve()
            assert target.is_relative_to(skill_file.parent.resolve()), link
            assert target.is_file(), link
            if "references/examples/" in link:
                assert target.is_relative_to(skill_root), link
                assert target in expected_paths(), link
        for filename in filenames:
            target = (skill_file.parent / "references/examples" / filename).resolve()
            assert target.is_relative_to(skill_root)


def test_repository_suite_includes_example_checks() -> None:
    checks = (ROOT / "scripts/run_checks.py").read_text(encoding="utf-8")
    assert '("example tests", "tooling/test_examples.py")' in checks


def main() -> int:
    test_expected_examples_exist()
    test_examples_have_required_sections()
    test_examples_require_adaptation_and_label_handoffs()
    test_sibling_examples_have_distinct_content()
    test_example_pointers_and_index_links_resolve()
    test_example_links_stay_inside_owning_skill()
    test_repository_suite_includes_example_checks()
    print("Example tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
