#!/usr/bin/env python3
"""Exercise the portable deep-bug-audit efficiency scorer."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCORER = ROOT / "skills" / "deep-bug-audit" / "scripts" / "audit_efficiency_score.py"


def run_scorer(payload: dict, *args: str) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as temporary:
        path = pathlib.Path(temporary) / "report.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(SCORER), str(path), "--json", *args],
            text=True,
            capture_output=True,
            check=False,
        )


def test_scalar_self_reported_counts_are_ignored() -> None:
    result = run_scorer({
        "severity_counts": {"critical": 99, "high": 99},
        "suspected": 99,
        "duplicates": 99,
        "files_reviewed": 999,
        "commands_run": 999,
        "paths": 999,
        "findings": [],
    })
    assert result.returncode == 0, result.stderr
    scored = json.loads(result.stdout)
    assert scored["total_findings"] == 0
    assert scored["files_reviewed"] == 0
    assert scored["commands_run"] == 0
    assert "files_reviewed" in scored["untrusted_count_fields_ignored"]


def test_json_counts_come_from_enumerated_evidence() -> None:
    result = run_scorer({
        "findings": [{
            "severity": "high",
            "evidence": ["src/service.py:12"],
            "verifier": "python3 tests/test_service.py",
            "required_regression": "test_missing_field",
            "mutation": "invert guard",
        }],
        "reviewed_files": ["src/service.py", "tests/test_service.py"],
        "verified_commands": ["python3 tests/test_service.py"],
        "target_paths": ["src"],
    })
    assert result.returncode == 0, result.stderr
    scored = json.loads(result.stdout)
    assert scored["total_findings"] == 1
    assert scored["files_reviewed"] == 2
    assert scored["commands_run"] == 1
    assert scored["paths"] == 1
    assert scored["evidence_completeness"] == 1.0
    assert scored["reproducibility"] == 1.0


def test_markdown_paths_are_not_limited_to_known_project_directories() -> None:
    report = """
### 1. High: bad contract
Evidence: `packages/payments/handler.ts:44`
Verifier: `node checks/payments.js`
Required regression: `specs/payments.spec.ts`
Mutation: drop the field
"""
    with tempfile.TemporaryDirectory() as temporary:
        path = pathlib.Path(temporary) / "report.md"
        path.write_text(report, encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(SCORER), str(path), "--json"],
            text=True,
            capture_output=True,
            check=False,
        )
    assert result.returncode == 0, result.stderr
    scored = json.loads(result.stdout)
    assert "packages/payments/handler.ts:44" in scored["observed_files"]
    assert "specs/payments.spec.ts" in scored["observed_files"]
    assert scored["commands_run"] == 1
    assert any("node checks/payments.js" in command for command in scored["observed_commands"])


def test_malformed_findings_shape_is_bounded_without_traceback() -> None:
    result = run_scorer({"findings": None, "files_reviewed": 999, "commands_run": 999, "paths": 999})
    assert result.returncode == 0, result.stderr
    assert "Traceback" not in result.stderr
    assert json.loads(result.stdout)["total_findings"] == 0


def test_cli_flags_emit_one_deprecation_warning() -> None:
    result = run_scorer(
        {"findings": [], "reviewed_files": [], "verified_commands": [], "target_paths": []},
        "--files-reviewed", "5", "--commands-run", "3", "--paths", "2",
    )
    assert result.returncode == 0, result.stdout
    assert "self-reported count flags are ignored" in result.stderr
    assert result.stderr.count("counts are derived from enumerated evidence") == 1
    json.loads(result.stdout)


def test_no_warning_without_deprecated_flags() -> None:
    result = run_scorer({"findings": [], "reviewed_files": [], "verified_commands": [], "target_paths": []})
    assert result.returncode == 0, result.stdout
    assert result.stderr == ""


if __name__ == "__main__":
    for name, value in sorted(globals().items()):
        if name.startswith("test_"):
            value()
    print("Deep bug audit scorer tests passed")
