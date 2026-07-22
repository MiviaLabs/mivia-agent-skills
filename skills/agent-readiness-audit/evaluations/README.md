# agent-readiness-audit evaluation evidence

This skill incorporates the immutable `agent_readiness_audit@2.0.3` prompt from
the Mivia evals repository. The prompt version is recorded in `prompt-meta.yaml`.

## Why this prompt is installed

Version 2.0.3 is the 100-case paid release-gates winner. It adds a hard
clean-default (presence is not ENFORCED), language/project-agnostic control-plane
framing, action-verdict calibration (BLOCKED vs CONDITIONAL), and explicit
rules that instruction files are a control surface and policy text alone is
never `ENFORCED`.

## Dataset and tests

The release suite is `agent_readiness_audit_regression` (splits v1.0.0):

- 100 cases: train/dev/holdout mix (see `datasets/splits.yaml`).
- 75 defect / 25 clean polarity cases (control-plane bundles, not source languages).
- Mechanisms: docs-only policy, uninstalled hooks, contradicted policy, optional
  CI, NOT_RUN checks, overgrant push/merge, secrets unprotected, autonomy caps,
  partial local hooks, true-supported read-only, adversarial looks-enforced,
  GATED missing evidence, NOT_ASSESSED empty surface, scope-creep app bugs,
  multi-control mixes.

Authoritative suite, oracle (`agent_readiness_oracle`), and scoring live in
`mivia-evals`. This repository vendors the suite and splits under `datasets/` so
installable skill packages carry the evidence corpus without requiring a
checkout of mivia-evals.

Activation evaluations (`*.json` in this directory) check when the skill should
trigger; they are not the 100-case paid suite.

## Runs and result

Paid run `20260722T080023Z-6bb8461d` used Gemini Flash Lite as the target and
DeepSeek V4 Flash as the judge on the 100-case suite. It passed all release
gates:

| Metric | Result | Gate |
| --- | ---: | ---: |
| Aggregate pass rate | 0.960 | >= 0.90 |
| Clean false-positive rate | 0.0 | <= 0.03 |
| Critical-defect recall | 0.976 | >= 0.90 |
| Unsupported security/tenant findings | 0 | 0 |

Trajectory: 2.0.0 pass 0.22 -> 2.0.1 0.54 -> 2.0.2 0.80 -> **2.0.3 0.96 (gates green)**.

Source references (upstream):

- Prompt: `mivia-evals/prompts/agent_readiness_audit/2.0.3/prompt.md`
- Suite: `mivia-evals/suites/agent_readiness_audit_regression.yaml`
- Splits: `mivia-evals/campaigns/agent_readiness_audit/splits.yaml`
- Results: `mivia-evals/campaigns/agent_readiness_audit/PAID_EVAL_RESULTS.md`
- Local copies: `datasets/suite.yaml`, `datasets/splits.yaml`
