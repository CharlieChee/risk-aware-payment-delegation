# Results and evidence map

All commands below are offline. They do not call a model, overwrite a response,
or replace the recorded outcomes with a different scoring convention.

| Result | Input and cohort selector | Operation and scope |
|---|---|---|
| Primary comparison | `paper/data/derived/main_rows.json`, primary `paper/data/supplements/`, and `paper/data/author_reports/`; 200 tasks per method/configuration | `python paper/scripts/make_tables.py` reconstructs the displayed counts from the designated trial or aggregate inputs. These sources are separate cohorts, not interchangeable rows. |
| Raw DeepSeek primary decisions | `bilingual/raw_records/manifest.json`; all 800 Direct/Set records | `python scripts/verify_raw_records.py` checks hashes, unaltered response content, and stored scoring alignment. |
| Generic prompt and four-route controls | `bilingual/prompt_controls/manifest.json`, `paper/data/supplements/prompt_controls_20261011/cohorts.json` | `python scripts/verify_prompt_controls.py` verifies the controlled prompt change and rescores 3,520 retained final decisions. It does not rerun generated programs. |
| Retained-intent comparison | `paper/data/supplements/intent_ambiguity_20261011/parameter_rows.json`; DeepSeek low/max, GLM low, and Qwen Max low, using the complete partitions selected by `intent_ambiguity_reporting.py` | `python paper/scripts/intent_ambiguity_reporting.py` recomputes 294 paired method outcomes (147 task-configuration units). |
| Observed method example | `bilingual/observed_trace/manifest.json`; F02a/F02b, clean context, first Set sample, Astra max | `python scripts/verify_observed_trace.py` checks original-output identity and repeats deterministic execution of the two archived specifications. Translations and abbreviated symbols are display transformations only. |
| Frozen-rule diagnosis | `paper/data/diagnostics/stress_summary.json` and `stress_chart_data.json`; DeepSeek low/high/max, three realizations | The reporting builder pools 648 frozen artifacts and 1,296 recorded replays. The reference-assisted intervention summary uses `paper/data/supplements/intent_ambiguity_20261011/omitted_referent.json`; the 16 selected outputs are not independent requests. |
| Complete-domain certification | `risk_payment/decision.py`, historical `risk_payment/engine.py`, and `paper/reporting_checks/semantic_revision_audit.json` | The manuscript distinguishes action agreement from the complete-domain guarantee. The audit records inspected cohorts, source hashes, and unresolved reason codes; it does not change their outcomes. |
| Effort and language | `paper/data/derived/grid_summary.json`, `language_all_methods_matched.json`, and the explicitly supplied aggregate language updates | Rebuild all 19 complete GPT-5.6 settings, including Sol ultra. The 60-task language records and 200-task aggregate panel remain separate. Equal aggregate counts do not establish identical response text or language invariance. |
| Figures and manuscript | `paper/figures/*_values.json`, table builders, and frozen reporting inputs | `python reproduce.py --pdf` runs the release checks and rebuilds the paper. Add `--verify-references` to verify the 200 synthetic reference tasks with two implementations. |

## Cohort accounting

The retained-intent reporting code keeps the legacy name
`figure3_complete_results.json`; it supplies Figure 2 in the revised manuscript.

The intent API archive has 544 recorded outcomes: 294 in the complete paired
Direct/Set panel, 178 merged-expression controls, and 72 Direct/Set outcomes
from other configurations without a complete paired panel. A separate 72-row
native stress panel brings this historical collection to 616. The 36-call
input intervention is another experiment. No aggregate sum is an independent
task denominator.

The complete effort study contains 25 configurations and three realizations,
each with 60 outcomes. The displayed GPT-5.6 subset contains seven Sol, six
Terra, and six Luna settings. Its 19 configurations include Sol ultra; the
earlier off-through-max table contained only 18.

## Version and provenance fields

Raw manifests carry source and exported-shard SHA-256 hashes. Request records
retain the requested model, recorded settings, original messages, and retry
or transport metadata where present. Transport records retain the returned
model identifier when the provider exposes it; missing identifiers are not
filled retrospectively. The release manifest hashes the evaluation and
reporting code supplied with the paper. `docs/protocol.md` describes the
preserved protocol; `docs/reproduction.md` separates offline reconstruction,
reference verification, and new inference runs.

Reconstructing a figure from aggregate inputs is not raw-response rescoring.
Likewise, a hash or a successful interpreter run does not certify that generated
conditions faithfully express the request. The paper's rule and component
diagnostics address that separate semantic question.
