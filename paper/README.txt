RISK-AWARE PAYMENT DELEGATION
From Intent to Executable Decisions

Main text: 8 pages. Full manuscript: 23 pages.
Four main figures report boundary decisions, retained-intent decisions,
frozen-rule diagnosis, and reasoning-setting/task-language results.
All four figures use grayscale, with hatching, line styles, and markers
to distinguish series. Hyperlinks use #000099 without borders or underlines.
The abstract contains plain text; abstract.txt is ready for submission metadata.
A dedicated analysis section distinguishes action safety from authorization-domain
soundness and examines state omission, candidate availability, and utility ranking.
Observed insurance and ticket compilations are in the appendix. Main-text tables
report component interventions and 36 input-intervention generations for one
ambiguous request. No model calls were added in
this editorial revision. Original numerical reporting inputs are unchanged.

Offline reproduction (no model calls):
  python -m pip install -r requirements.txt
  python reproduce.py --pdf
Omit --pdf for reporting and deterministic contract checks without TeX.

Compile the modular manuscript:
  latexmk -pdf -interaction=nonstopmode -halt-on-error paper.tex
In Overleaf select paper.tex and pdfLaTeX. paper_all_in_one.tex contains the
same text, tables, and bibliography, with external figure assets.

Contents:
  paper.tex, evaluation.tex, sections/   Editable manuscript
  abstract.txt                          Plain-text submission abstract
  tables/                               Generated reporting fragments
  figures/                              Vector figures and plotted values
  data/                                 Frozen per-study reporting inputs
  reporting_checks/                     Contract and provenance checks
  references_audit/                     Verified research-library metadata

The manuscript reports Set without an implementation-comparison branch.
The complete implementation controls, concrete syntax, and source groups
are retained in implementation_archive/ and reporting_checks/. The pooled
diagnostic table includes every original preparation stratum; these are not
identical repeated generations.
The current primary comparison has eleven 200-task configurations per method.
Historical per-trial cohorts and later aggregate updates remain separate.
The displayed intent panel has 294 method outcomes in 147 matched units;
544 describes its broader API campaign, including controls and other rows.
The GPT-5.6 effort table contains 18 settings, six per model family.
Reuse compares Direct per catalogue with Set rule reuse, not cached versus
uncached execution of one identical implementation.

Algorithm 1 certifies the compiled model on a complete resolved catalogue.
Primary DeepSeek decisions use this evaluator: 184/200 exact for low and
185/200 for high, totaling 369/400 (92.25%). The same decisions feed the
primary figure, error partitions, template counts, execution controls, and
paired bootstrap intervals. The replay is in
data/supplements/primary_certification_20261011/replay.json, and
scripts/certified_primary.py regenerates the reporting summaries.
The execution guarantee concerns generated conditions; their fidelity to the
request is evaluated through decisions and authorization-domain diagnostics.
The public repository's docs/evidence_map.md maps results to retained records,
scorers, and reproducibility levels. Aggregate reconstruction and response-level
rescoring are distinct. This source bundle reconstructs the manuscript.
The recorded primary trace is checked against the generated clause and all
14,592 candidate-event reference calculations, with no new model calls.
The public repository additionally contains the inference harness and raw
record collections. No credentials are included.

Official ACL style files are unchanged. The six appendices cover decision semantics,
benchmark/protocol, full results, ambiguity, controls/reuse, and diagnostics.
