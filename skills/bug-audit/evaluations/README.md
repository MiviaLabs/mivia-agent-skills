# bug-audit evaluation evidence

This skill incorporates the immutable `bug_audit@2.0.8` prompt from the Mivia
evals repository. The prompt version is recorded in `prompt-meta.yaml`.

## Why this prompt is installed

Version 2.0.8 added a hard clean-default preamble and expanded the clean cases
so the audit rejects false positives for language cleanup, parameterized SQL,
escaping, `Result` propagation, tenant scoping, mutex scope, cancellation,
and related correctness patterns. The prompt and suite were co-evolved so the
evaluation measures reachable defects, literal evidence, reachability, and
clean conclusions rather than brittle wording.

## Dataset and tests

The release suite is `bug_audit_regression`, using split definition 3.0.3:

- 100 cases: 33 train, 31 dev, 36 holdout.
- 75 bug cases and 25 clean cases.
- 34 critical cases.
- Languages: Go 19, Python 20, TypeScript 18, Java 15, C# 14, Rust 14.
- Mechanisms include resource cleanup, contract drift, concurrency, retries,
  cancellation, persistence, authz, tenant isolation, injection, SSRF,
  deserialization, unsafe parsers, and adversarial clean patterns.

The authoritative dataset and scoring implementation remain in
`mivia-evals`; this repository records the release metadata and result summary
so installed skill users can understand the evidence without treating it as a
new local test suite.

## Runs and result

Paid run `20260721T235247Z-db19d328` used Gemini Flash Lite as the target and
DeepSeek V4 Flash as the judge on the 100-case suite. It passed all release
gates:

| Metric | Result | Gate |
| --- | ---: | ---: |
| Aggregate pass rate | 0.920 | >= 0.90 |
| Clean false-positive rate | 0.0 | <= 0.03 |
| Critical-defect recall | 0.971 | >= 0.90 |
| Unsupported security/tenant findings | 0 | 0 |

Earlier 2.0.6 and 2.0.7 runs on the expanded suite failed release gates,
primarily because of clean false positives. The 2.0.8 run is the active pin;
residual failures were mostly severity-boundary misses and did not break the
release gates.

Source references:

- Prompt: `/home/mac/mivialabs/mivia-evals/prompts/bug_audit/2.0.8/prompt.md`
- Suite: `/home/mac/mivialabs/mivia-evals/suites/bug_audit_regression.yaml`
- Splits: `/home/mac/mivialabs/mivia-evals/campaigns/bug_audit/splits.yaml`
- Results: `/home/mac/mivialabs/mivia-evals/campaigns/bug_audit/PAID_EVAL_RESULTS.md`
