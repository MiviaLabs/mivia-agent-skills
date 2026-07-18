# Prompt-eval evidence for the verify-code-change improvement

These HTML reports are the eval-run evidence behind the SKILL.md change in this
branch (scope-calibrated PASS/PARTIAL result semantics). They are provenance
only: not activation evaluations (those are the `*.json` files one level up),
and not propagated to target repos on install.

## What was measured

A distilled single-shot subset of this skill's verification discipline was
turned into a versioned prompt and scored with the mivia-evals harness across a
fixed 6-case suite (a clean focused change, a migration whose required
verification is unavailable, a wrong-method trap, an under-classified shared
helper, a passing-test-but-collateral-defect diff, and a non-code control).
Deterministic code checks covered presence-based discipline; an LLM judge,
fenced to grade against the scenario facts rather than its own beliefs, scored
blast-radius calibration, evidence honesty, method appropriateness, diff-review
vigilance, and residual-risk gating.

Scope note: this measures the model's verification reasoning and reporting
discipline on a described scenario, not whether verification was actually
performed end to end (a text harness cannot run tests or builds). Treat it as
targeted prompt-quality signal, not proof of runtime verification.

## Result

| Version | Runs | Combined score |
| --- | --- | --- |
| v1.0.0 (baseline) | 0.54, 0.83 | mean ~0.69 |
| v1.1.0 (winner) | 0.87, 1.00 | mean ~0.93 |

v1.1.0's worst run tops v1.0.0's best. The change folded into SKILL.md is the
scope-calibrated PASS/PARTIAL guidance: return PASS when the checks required at
the change's blast radius passed (do not manufacture higher-tier "not run"
gaps), and return PARTIAL/FAIL when the diff review finds a material defect in
the change itself. The baseline's other apparent miss was a harness artifact
(a decoration-strict regex and a truncating token cap), fixed in the harness,
not the skill.

## Honest caveats

Judge and target were free-tier models, so absolute scores carry noise; two
runs in the wider campaign died on transient provider errors and are not
included. The version ranking is stable on clean runs. Image/agentic execution
behavior is out of scope for this text harness.

## Reports

Each is a self-contained HTML file in this directory; open it directly.

- Baseline that first exposed the harness artifacts: `v1.0.0-baseline-25c1d1c9.html`
- v1.0.0 head-to-head runs: `v1.0.0-run-a-52668e69.html`, `v1.0.0-run-b-6bface8e.html`
- v1.1.0 winner runs: `v1.1.0-run-a-ed2aac18.html`, `v1.1.0-run-b-11824002.html`
