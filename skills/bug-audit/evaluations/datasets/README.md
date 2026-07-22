# Vendored eval dataset (bug-audit)

Copied from `mivia-evals` for packaging and offline inspection.

| File | Upstream |
| --- | --- |
| `suite.yaml` | regression suite (100 cases) |
| `splits.yaml` | train/dev/holdout + lineage registry |
| `mock_by_case_id.json` | offline mock responses that pass hidden oracles |

These files are **evidence and packaging**, not a local runner. Score with
`mivia-evals` (`mivia eval run --suite ...`).

Do not edit in place to green results; update from mivia-evals when the
campaign advances.
