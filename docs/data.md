# Data guide and provenance

## Reading the evidence

The release distinguishes task definitions, historical per-trial evidence,
derived reporting tables, and author-provided aggregate updates. This avoids
treating a figure's displayed count as an independent raw model response.

| Location | Unit and use |
|---|---|
| `benchmarks/primary/manifest.json` | 200 tasks, including 100 matched feasibility pairs; references are evaluation-only |
| `benchmarks/intent/cases.json` | 66 numerical/context variants across three intent families; 42 API variants and 24 stress variants |
| `bilingual/language_panel/` | 60 underlying tasks in two languages, with identical candidate values |
| `data/artifacts/manifest.json` | 8,046 retained Direct/Set artifact projections in compressed JSONL shards |
| `paper/data/derived/` | Historical scored rows and per-cohort summaries; these include archived implementation controls |
| `paper/data/supplements/` | Model extensions, partial snapshots, and retained-intent evaluations |
| `paper/data/diagnostics/` | Frozen-rule replay and reference-assisted interventions |
| `paper/data/author_reports/` | Later externally supplied aggregate updates and adjudications |

The Figure 3 cohorts contain 294 Direct/Set outcomes in four complete matched
comparisons. The broader retained-intent archive contains 616 method outcomes
and 36 input interventions. These are repeated evaluations, not hundreds of
independent ambiguity types. Model settings and cohorts overlap; do not sum
them into a headline number of independent examples.

## Language and publication transformations

Outside `bilingual/`, human-facing assets are English. The primary English
requests reuse reviewed translations from the language experiment; all 200
catalogues, numeric attributes, and reference answers are unchanged.
`benchmarks/primary/provenance.json` maps original and released hashes.

The 66 intent variants are English translations for inspection and new runs.
They are not new English-language measurements of the archived Chinese runs.
`bilingual/intent_translation_pairs.json` contains the source/translation audit,
including contextual distractors and scoring instructions. Numerical tokens
are checked across every translated pair. Original Chinese prompts and their
English release counterparts are kept in the bilingual prompt audit.

Reporting projections remove untranslated narrative-only explanations and
machine-specific paths. Counts, numerical inputs, decision fields, formulas,
and failure outcomes are preserved. State labels may be replaced by stable
English identifiers; labels do not determine the evaluator's mathematical
semantics. Every exported artifact includes the source observation and content
hash. The field-level projection inventories record omitted narrative fields.
These are parsed-output projections, not byte-identical raw transcript exports.

## Aggregate updates

Some current paper counts were supplied from experiments on another computer
and are stored as aggregate reports. The local historical snapshots are kept
separately, even where their counts differ. In this release, the external
per-trial records underlying those updates are not included; the explicit
`raw_records_received` and reconciliation fields preserve that distinction.
The reporting scripts can reconstruct the displayed tables and figures from
the supplied counts, but those particular external outcomes cannot be rescored
from the archived local responses. No responses, error breakdowns, or template
assignments are invented to fill that gap.

The requested model/configuration inventory covers 12 model identifiers and
52 model--effort settings. It describes observed request coverage, including
exploratory and partial batches, not 52 complete primary comparisons.

## Artifact access

```python
import gzip, json
from pathlib import Path

for shard in Path("data/artifacts").glob("*.jsonl.gz"):
    with gzip.open(shard, "rt", encoding="utf-8") as stream:
        for line in stream:
            record = json.loads(line)
            # Inspect record["parsed_artifact"], outcome, usage, and source hashes.
```

Development-only scheduling logs, credentials, personal workstation paths,
unrelated benchmark repositories, and copyrighted source-paper PDFs are not
part of this release. The original local experiment archive is unchanged.
