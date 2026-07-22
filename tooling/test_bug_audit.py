#!/usr/bin/env python3
"""Validate the installed bug-audit prompt and evaluation evidence."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "bug-audit"


def test_skill_identity_and_eval_evidence() -> None:
    skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    evidence = (SKILL / "evaluations" / "README.md").read_text(encoding="utf-8")
    assert "name: bug-audit" in skill
    assert "Hard clean-default" in skill
    assert "20260721T235247Z-db19d328" in evidence
    assert "100 cases" in evidence


def test_prompt_requires_clean_default() -> None:
    skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    assert "No real bug was found." in skill


def test_prompt_has_required_finding_contract() -> None:
    skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    for section in ("Contract violated:", "Evidence:", "Reachable path:", "Impact:", "Regression:"):
        assert section in skill


def test_prompt_has_eval_version() -> None:
    meta = (SKILL / "evaluations" / "prompt-meta.yaml").read_text(encoding="utf-8")
    assert 'version: "2.0.8"' in meta


if __name__ == "__main__":
    for name, value in sorted(globals().items()):
        if name.startswith("test_"):
            value()
    print("Bug audit skill tests passed")
