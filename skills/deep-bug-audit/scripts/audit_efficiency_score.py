#!/usr/bin/env python3
"""Score deep bug-audit efficiency from markdown, JSON, or stdin.

The score is intentionally simple and explainable. It rewards confirmed,
high-impact findings, evidence completeness, verifier coverage, and mutation
quality while making elapsed time and reviewed scope visible.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any


SEVERITY_WEIGHTS = {
    "critical": 13,
    "high": 8,
    "medium": 4,
    "low": 1,
}


def read_input(path: str | None) -> str:
    if not path or path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def observed_path_tokens(text: str) -> list[str]:
    """Return plausible repository-relative paths without project assumptions."""
    pattern = re.compile(
        r"(?<![\w.-])((?:\./|\.\./|[A-Za-z0-9_.-]+/)[A-Za-z0-9_.:/-]+)"
    )
    paths = set()
    for match in pattern.finditer(text):
        token = match.group(1).rstrip("`.,;)]}")
        if token.startswith(("http://", "https://", "file://")):
            continue
        if token in {"./", "../"}:
            continue
        paths.add(token)
    return sorted(paths)


def parse_markdown(text: str) -> dict[str, Any]:
    severity_counts = {severity: 0 for severity in SEVERITY_WEIGHTS}
    finding_heading = re.compile(
        r"(?im)^\s*(?:#{2,6}\s*)?(?:\d+[.)]\s*)?"
        r"(?:(critical|high|medium|low)\s*:|severity\s*:\s*(critical|high|medium|low)\b)"
    )
    for match in finding_heading.finditer(text):
        severity = (match.group(1) or match.group(2)).lower()
        severity_counts[severity] += 1

    if sum(severity_counts.values()) == 0:
        labeled = re.compile(r"(?im)^\s*[-*]\s*severity\s*:\s*(critical|high|medium|low)\b")
        for match in labeled.finditer(text):
            severity_counts[match.group(1).lower()] += 1

    sections = {
        "evidence": len(re.findall(r"(?im)^\s*(?:evidence|source evidence)\s*:", text)),
        "verifier": len(re.findall(r"(?im)^\s*(?:verifier|verification|commands? run)\s*:", text)),
        "missing_test": len(re.findall(r"(?im)^\s*(?:why tests missed|missing test|required regression)\s*:", text)),
        "mutation": len(re.findall(r"(?im)^\s*(?:mutation|mutations? that must fail)\s*:", text)),
    }
    suspected = len(re.findall(r"(?i)\bsuspected\b", text))
    duplicates = len(re.findall(r"(?i)\b(?:duplicate|known finding|known blocker|already covered)\b", text))
    observed_files = observed_path_tokens(text)
    observed_commands = sorted(set(
        line.strip() for line in text.splitlines()
        if re.search(
            r"\b(?:go\s+(?:test|vet)|cargo\s+(?:test|clippy)|pytest|ruff|pylint|"
            r"tsc|clang-tidy|python(?:3)?|node|npm|pnpm|yarn|bun|make|bazel|"
            r"mvn|gradle|dotnet|curl|docker|podman|terraform|kubectl)\b",
            line,
            re.IGNORECASE,
        )
    ))
    observed_paths = sorted(set(
        item.removeprefix("./").split("/", 1)[0] for item in observed_files
    ))
    return {
        "severity_counts": severity_counts,
        "sections": sections,
        "suspected": suspected,
        "duplicates": duplicates,
        "observed_files": observed_files,
        "observed_commands": observed_commands,
        "observed_paths": observed_paths,
        "untrusted_count_fields": [],
    }


def parse_json_report(text: str) -> dict[str, Any]:
    raw = json.loads(text)
    if not isinstance(raw, dict):
        raise ValueError("JSON report must be an object")
    severity_counts = {severity: 0 for severity in SEVERITY_WEIGHTS}
    sections = {key: 0 for key in ("evidence", "verifier", "missing_test", "mutation")}
    findings = raw.get("findings", [])
    if not isinstance(findings, list):
        findings = []

    for finding in findings:
        if not isinstance(finding, dict):
            continue
        severity = str(finding.get("severity", "")).lower()
        if severity in severity_counts:
            severity_counts[severity] += 1
        if finding.get("evidence"):
            sections["evidence"] += 1
        if finding.get("verifier") or finding.get("verification"):
            sections["verifier"] += 1
        if finding.get("missing_test") or finding.get("required_regression"):
            sections["missing_test"] += 1
        if finding.get("mutation"):
            sections["mutation"] += 1

    observed_files = raw.get("reviewed_files", [])
    observed_commands = raw.get("verified_commands", raw.get("verifiers", []))
    observed_paths = raw.get("target_paths", [])
    if not isinstance(observed_files, list):
        observed_files = []
    if not isinstance(observed_commands, list):
        observed_commands = []
    if not isinstance(observed_paths, list):
        observed_paths = []
    return {
        "severity_counts": severity_counts,
        "sections": sections,
        "suspected": sum(1 for finding in findings if isinstance(finding, dict) and finding.get("status") == "suspected"),
        "duplicates": sum(1 for finding in findings if isinstance(finding, dict) and finding.get("status") in {"duplicate", "known"}),
        "elapsed_minutes": raw.get("elapsed_minutes"),
        "observed_files": sorted({str(item) for item in observed_files}),
        "observed_commands": sorted({str(item) for item in observed_commands}),
        "observed_paths": sorted({str(item) for item in observed_paths}),
        "untrusted_count_fields": ["severity_counts", "suspected", "duplicates", "files_reviewed", "commands_run", "paths"],
    }


def parse_report(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("{"):
        try:
            return parse_json_report(stripped)
        except json.JSONDecodeError:
            pass
    return parse_markdown(text)


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def coalesce_number(*values: Any, default: float = 0.0) -> float:
    for value in values:
        if value is None:
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    return default


def score(parsed: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    severity_counts = parsed["severity_counts"]
    total_findings = sum(severity_counts.values())
    weighted_findings = sum(SEVERITY_WEIGHTS[k] * v for k, v in severity_counts.items())

    elapsed_minutes = coalesce_number(args.elapsed_minutes, parsed.get("elapsed_minutes"), default=0.0)
    files_reviewed = float(len(parsed.get("observed_files", [])))
    commands_run = float(len(parsed.get("observed_commands", [])))
    paths = float(len(parsed.get("observed_paths", [])) or 1)

    sections = parsed["sections"]
    denominator = max(total_findings, 1)
    evidence_completeness = sum(clamp(sections[key] / denominator) for key in sections) / len(sections)

    verifier_density = clamp(commands_run / max(total_findings, 1))
    mutation_density = clamp(sections["mutation"] / denominator)
    reproducibility = (verifier_density * 0.45) + (mutation_density * 0.35) + (evidence_completeness * 0.20)

    expected_files = max(paths, 1.0) * 20.0
    scope_sampling = clamp(files_reviewed / expected_files) if files_reviewed else 0.0

    elapsed_hours = elapsed_minutes / 60.0 if elapsed_minutes > 0 else 0.0
    weighted_per_hour = weighted_findings / elapsed_hours if elapsed_hours else None
    high_plus = severity_counts["critical"] + severity_counts["high"]
    high_plus_per_hour = high_plus / elapsed_hours if elapsed_hours else None

    scope_penalty = 1.0 + (0.25 * math.log2(max(paths, 1.0)))
    efficiency_index = None
    if elapsed_hours:
        efficiency_index = (
            (weighted_findings / elapsed_hours)
            * (0.55 + 0.45 * evidence_completeness)
            * (0.70 + 0.30 * reproducibility)
            / scope_penalty
        )

    return {
        "severity_counts": severity_counts,
        "total_findings": total_findings,
        "weighted_findings": round(weighted_findings, 2),
        "elapsed_minutes": elapsed_minutes,
        "files_reviewed": int(files_reviewed),
        "commands_run": int(commands_run),
        "paths": int(paths),
        "evidence_completeness": round(evidence_completeness, 3),
        "reproducibility": round(reproducibility, 3),
        "scope_sampling": round(scope_sampling, 3),
        "weighted_findings_per_hour": None if weighted_per_hour is None else round(weighted_per_hour, 2),
        "high_plus_findings_per_hour": None if high_plus_per_hour is None else round(high_plus_per_hour, 2),
        "efficiency_index": None if efficiency_index is None else round(efficiency_index, 2),
        "suspected_mentions": parsed.get("suspected", 0),
        "duplicate_or_known_mentions": parsed.get("duplicates", 0),
        "observed_files": parsed.get("observed_files", []),
        "observed_commands": parsed.get("observed_commands", []),
        "observed_paths": parsed.get("observed_paths", []),
        "untrusted_count_fields_ignored": parsed.get("untrusted_count_fields", []),
    }


def render_markdown(result: dict[str, Any]) -> str:
    lines = [
        "Audit efficiency summary:",
        f"- Findings: {result['total_findings']} (critical={result['severity_counts']['critical']}, high={result['severity_counts']['high']}, medium={result['severity_counts']['medium']}, low={result['severity_counts']['low']})",
        f"- Weighted findings: {result['weighted_findings']}",
        f"- Elapsed minutes: {result['elapsed_minutes']}",
        f"- Files reviewed: {result['files_reviewed']}",
        f"- Commands run: {result['commands_run']}",
        f"- Evidence completeness: {result['evidence_completeness']}",
        f"- Reproducibility: {result['reproducibility']}",
        f"- Scope sampling: {result['scope_sampling']}",
    ]
    if result["weighted_findings_per_hour"] is not None:
        lines.append(f"- Weighted findings/hour: {result['weighted_findings_per_hour']}")
    if result["high_plus_findings_per_hour"] is not None:
        lines.append(f"- Critical+high findings/hour: {result['high_plus_findings_per_hour']}")
    if result["efficiency_index"] is not None:
        lines.append(f"- Efficiency index: {result['efficiency_index']}")
    if result["suspected_mentions"] or result["duplicate_or_known_mentions"]:
        lines.append(f"- Exclusion signals: suspected_mentions={result['suspected_mentions']}, duplicate_or_known_mentions={result['duplicate_or_known_mentions']}")
    return "\n".join(lines)


def warn_ignored_args(args: argparse.Namespace) -> None:
    """Warn once when deprecated self-reported count flags are supplied."""
    ignored = []
    if getattr(args, "files_reviewed", None) is not None:
        ignored.append("--files-reviewed")
    if getattr(args, "commands_run", None) is not None:
        ignored.append("--commands-run")
    if getattr(args, "paths", None) is not None:
        ignored.append("--paths")
    if not ignored:
        return
    print(
        "audit-efficiency-score: self-reported count flags are ignored; counts are derived from enumerated evidence in the report.",
        file=sys.stderr,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Score deep bug-audit efficiency.")
    parser.add_argument("report", nargs="?", help="Markdown or JSON report path, or '-' for stdin.")
    parser.add_argument("--elapsed-minutes", type=float, help="Elapsed audit time in minutes.")
    parser.add_argument("--files-reviewed", type=int, help="Deprecated self-reported file count.")
    parser.add_argument("--commands-run", type=int, help="Deprecated self-reported command count.")
    parser.add_argument("--paths", type=int, default=None, help="Deprecated self-reported path count.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of markdown.")
    args = parser.parse_args()
    warn_ignored_args(args)

    try:
        text = read_input(args.report)
        parsed = parse_report(text)
        result = score(parsed, args)
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        print(f"audit-efficiency-score: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(render_markdown(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
