# Prompt-eval evidence for the deep-bug-audit improvements

These HTML reports are the eval-run evidence that drove the SKILL.md changes in
commit `feat(deep-bug-audit): per-resource verify, current-runtime guard,
no-finding clause`. They are provenance only. They are not activation
evaluations (those are the `*.json` files one level up) and they are not
propagated to target repos on install.

## What was measured

A distilled, single-shot subset of this skill's audit instructions (Objective,
Finding Format, severity guide, verification standard) was turned into a
versioned prompt and scored across three versions with the mivia-evals harness.
Each version ran against a fixed 5-case Go-snippet suite: three cases with a
real planted bug, one clean control (no bug), one nuanced case. A code check
gated the Finding Format; an LLM judge scored bug-identification accuracy,
severity calibration, evidence groundedness, and appropriate uncertainty.

Scope note: this measures instruction-following, format compliance, and
single-snippet bug identification. It does not exercise the full agentic audit
(multi-file boundary mapping, the static-analyzer gate, reachability tracing
across a codebase). Treat it as targeted prompt-quality signal, not proof of
end-to-end audit quality.

## Results (valid-case mean, higher is better)

| Version | Runs | Valid-case means | Verdict |
| --- | --- | --- | --- |
| v1.0.0 (baseline) | 3 | 0.81, 0.96, 0.96 | high but swings; hallucinated a resource-leak on one run |
| v1.1.0 | 2 | 0.92, 0.65 | fixed the hallucination but drifted off the Finding Format |
| v1.2.0 | 3 | 0.99, 0.95, 0.90 | winner: highest mean and tightest spread, every run at or above 0.90 |

## What each change came from

- Per-resource independent verification (quote the line before asserting):
  v1.0.0 conflated two separate cleanup sites in one function and reported a
  nonexistent nil-close bug while missing the real temp-file leak. See
  `v1.0.0-baseline-b61b62dd.html`, case `defer_removed_leak`.
- Assume a current language runtime: the free-tier judge model wrongly flagged
  an un-stopped `time.After` timer inside a `select` as a leak, which is stale
  pre-Go-1.23 folklore. It scored the correct "no bug" answer at zero and
  inverted the signal on the better prompts. The guard reduces the target model
  making the same class of stale-version false positive.
- No-finding clause (say so plainly, do not fabricate): v1.1.0 sometimes
  replaced the Finding Format with free-form prose. The explicit output
  contract in v1.2.0 stabilized it.

## Honest caveats

- The judge and target were free-tier models, so absolute scores carry real
  noise. Two additional runs (not included here) died on transient provider
  errors, and one control case was penalized by a judge that was itself wrong
  about Go timer semantics. The ranking holds on the four cases not affected by
  that broken control, which is where the version-to-version decision was made.
- A stronger paid judge would give a more trustworthy absolute number. Within
  the free-tier noise floor, v1.2.0 was consistently the most robust.

## Reports

- Baseline that first exposed the failures: [v1.0.0-baseline-b61b62dd.html](v1.0.0-baseline-b61b62dd.html)
- v1.0.0 comparison runs: [a](v1.0.0-run-a-ffa5b065.html), [b](v1.0.0-run-b-580de8a2.html), [c](v1.0.0-run-c-410252e6.html)
- v1.1.0 comparison runs: [a](v1.1.0-run-a-01590ade.html), [b](v1.1.0-run-b-479714d8.html)
- v1.2.0 comparison runs: [a](v1.2.0-run-a-d6dce6ab.html), [b](v1.2.0-run-b-17a9a126.html), [c](v1.2.0-run-c-550e148e.html)
