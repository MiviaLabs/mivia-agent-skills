#!/usr/bin/env python3
"""Validate the installed agent-readiness-audit prompt and evaluation evidence."""

from __future__ import annotations

import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "agent-readiness-audit"


def test_skill_identity_and_eval_evidence() -> None:
    skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    evidence = (SKILL / "evaluations" / "README.md").read_text(encoding="utf-8")
    assert "name: agent-readiness-audit" in skill
    assert "Hard clean-default" in skill
    assert "20260722T080023Z-6bb8461d" in evidence
    assert "100 cases" in evidence


def test_prompt_has_control_plane_enums() -> None:
    skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    for token in (
        "ENFORCED",
        "DOCUMENTED_ONLY",
        "PARTIAL",
        "GATED",
        "NOT_RUN",
        "CONTRADICTED",
        "SUPPORTED_WITHIN_SCOPE",
        "BLOCKED",
        "NOT_ASSESSED",
    ):
        assert token in skill, token


def test_prompt_has_eval_version() -> None:
    meta = (SKILL / "evaluations" / "prompt-meta.yaml").read_text(encoding="utf-8")
    assert 'version: "2.0.3"' in meta


def test_vendored_dataset_present() -> None:
    datasets = SKILL / "evaluations" / "datasets"
    for name in ("suite.yaml", "splits.yaml", "mock_by_case_id.json", "README.md"):
        path = datasets / name
        assert path.is_file(), path
        assert path.stat().st_size > 100, path


def test_activation_evals_exist() -> None:
    evaluations = SKILL / "evaluations"
    for name in (
        "bounded-action-readiness.json",
        "repository-readiness.json",
        "ordinary-implementation.json",
        "non-agent-production-readiness.json",
    ):
        assert (evaluations / name).is_file(), name


if __name__ == "__main__":
    for name, value in sorted(globals().items()):
        if name.startswith("test_"):
            value()
    print("Agent readiness audit skill tests passed")
