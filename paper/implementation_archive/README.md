# Archived implementation controls

These materials preserve the implementation comparison and concrete syntax
that are no longer included in the manuscript. The archived TeX fragments
are documentation, not manuscript inputs. Their numbers and scoring conventions
are retained as recorded; they must not replace the current primary Set results.

The paper reports the original Set primary cohort, with the complete-domain
DeepSeek evaluation giving 184/200 and 185/200 exact decisions. It does not
select the better result from different implementations.

## Implementations and input conditions

Set uses generated state-wise expressions evaluated by a fixed procedure.
Set-Py generates an independent Python candidate-assessment function. It is
not a translation of a Set expression. Both use the same outer feasibility,
worst-case utility, and positive-value selection policy. The original labels
are preserved throughout the records:

| Record label | Preparation |
|---|---|
| `set` | State-wise specification; catalogue-independent preparation |
| `python_cached` | Procedural specification; catalogue-independent preparation |
| `python_fresh` | Procedural specification; catalogue-visible preparation |

Catalogue visibility and representation therefore differ across preparation
strata. These are not three identical replications. The frozen-rule diagnosis
holds each saved specification and its selector fixed between the mixed and
unsafe-only catalogues. It pools all three strata within each DeepSeek effort
setting, without removing failures or selecting outcomes by performance.

## Evidence and reconstruction

- `prior_execution_controls_section.tex` and the accompanying table fragments retain
  the previous implementation discussion and full numerical controls.
- `prior_formal_details.tex` retains concrete syntax, parsing, execution limits,
  and decision-contract details.
- `prior_authorization.tex` and `prior_appendix_replay.tex` retain the original
  nine source groups behind the diagnostic collection.
- `paper/data/diagnostics/stress_summary.json` and `stress_chart_data.json`
  preserve source groups and outcomes. `paper/reporting_checks/frozen_diagnostics_scope.json`
  maps the nine groups to the three effort rows in the paper.
- `paper/reporting_checks/execution_controls_values.json` and
  `prompt_controls_values.json` retain the implementation and four-route controls.
- `docs/prompt_controls.md` and `docs/evidence_map.md` map the record archives
  to their cohort selectors and verification operations.

Run `python paper/scripts/make_tables.py` to regenerate reporting summaries.
No model calls are made. Original responses, source labels, and archived scores
remain unchanged. Current manuscript figures use their designated reporting
inputs rather than this historical TeX archive.
