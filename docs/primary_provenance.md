# Primary-result provenance

The published primary comparison contains eleven configurations, with 200 tasks per method. `paper/scripts/primary_profiles.py::display_primary` selects the reporting inputs below. These are reporting sources, not a claim that every displayed result can be rescored from a raw response.

## Aggregate updates

`paper/data/author_reports/20261011_confirmed_aggregates.json` records externally supplied GLM high, Astra max, and Sol medium updates. `20261011_primary200_completion.json` completes their error partitions and useful-completion counts and supplies the completed 200-task Opus comparison. The latter report supersedes the earlier partial Opus display and supplies both displayed arms for the four configurations listed below. Sol Direct also matches the locally archived 200 observations (137 exact, 21 unsafe, 42 false refusals).

Original external responses and case-level classifications for the replacements have not been imported. Their aggregate counts can be reconstructed and checked for arithmetic consistency; case-level pairing, response rescoring, template breakdowns, and usage cannot be inferred from them. Historical local runs are retained as separate evidence.

## Arm-level source map

Paths below are relative to `paper/`. Local rows use the complete-domain reporting overlays where applicable; the input file is the reporting entry point.

| Configuration | Arm | Exact / 200 | Input | Evidence level |
|---|---|---:|---|---|
| DeepSeek low | Direct | 117 | `data/derived/main_summary.json` | Retained per-trial observations |
| DeepSeek low | SET | 184 | `data/derived/main_summary.json` | Retained per-trial observations |
| DeepSeek high | Direct | 131 | `data/derived/main_summary.json` | Retained per-trial observations |
| DeepSeek high | SET | 185 | `data/derived/main_summary.json` | Retained per-trial observations |
| Qwen Flash low | Direct | 66 | `data/supplements/qwen_primary200/summary.json` | Retained per-trial observations |
| Qwen Flash low | SET | 194 | `data/supplements/qwen_primary200/summary.json` | Retained per-trial observations |
| Qwen Max low | Direct | 59 | `data/supplements/qwen_primary200/summary.json` | Retained per-trial observations |
| Qwen Max low | SET | 87 | `data/supplements/qwen_primary200/summary.json` | Retained per-trial observations |
| GLM Flash low | Direct | 29 | `data/supplements/primary200_glm53_flash_low/summary.json` | Retained per-trial observations |
| GLM Flash low | SET | 136 | `data/supplements/primary200_glm53_flash_low/summary.json` | Retained per-trial observations |
| GLM high | Direct | 64 | `data/author_reports/20261011_primary200_completion.json` | External aggregate; raw import pending |
| GLM high | SET | 188 | `data/author_reports/20261011_primary200_completion.json` | External aggregate; raw import pending |
| 5.6 Luna medium | Direct | 41 | `data/supplements/primary200_gpt56_luna_medium/summary.json` | Retained per-trial observations |
| 5.6 Luna medium | SET | 91 | `data/supplements/primary200_gpt56_luna_medium/summary.json` | Retained per-trial observations |
| 5.6 Terra medium | Direct | 81 | `data/supplements/primary200_gpt56_terra_medium/summary.json` | Retained per-trial observations |
| 5.6 Terra medium | SET | 158 | `data/supplements/primary200_gpt56_terra_medium/summary.json` | Retained per-trial observations |
| 5.6 Sol medium | Direct | 137 | `data/author_reports/20261011_primary200_completion.json` | External aggregate; raw import pending |
| 5.6 Sol medium | SET | 196 | `data/author_reports/20261011_primary200_completion.json` | External aggregate; raw import pending |
| Astra max | Direct | 180 | `data/author_reports/20261011_primary200_completion.json` | External aggregate; raw import pending |
| Astra max | SET | 196 | `data/author_reports/20261011_primary200_completion.json` | External aggregate; raw import pending |
| Opus 5.5 medium | Direct | 142 | `data/author_reports/20261011_primary200_completion.json` | External aggregate; raw import pending |
| Opus 5.5 medium | SET | 194 | `data/author_reports/20261011_primary200_completion.json` | External aggregate; raw import pending |

The machine-readable map and frozen intent-parameter checks are in [`review_revision_evidence.json`](../paper/reporting_checks/review_revision_evidence.json). The primary template-bootstrap analysis uses retained DeepSeek observations; aggregate counts do not supply synthetic pairings.

## Verification boundaries

- Report reconstruction reproduces displayed counts from the designated inputs.
- Response rescoring applies the evaluator to a retained original response.
- Reference checking verifies consistency with the stipulated benchmark contract.

These checks answer different questions. The source map does not claim that numerical agreement between reference implementations establishes the semantics of unobserved merchant terms.
