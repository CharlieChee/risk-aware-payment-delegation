# Data guide

## Data organization

The release includes task definitions, archived trial records, reporting tables,
and aggregate summaries. These are separate data units with complementary uses.

| Location | Unit and use |
|---|---|
| `benchmarks/primary/manifest.json` | 200 tasks, including 100 matched feasibility pairs; references are evaluation-only |
| `benchmarks/intent/cases.json` | 66 numerical/context variants across three intent families; 42 API variants and 24 stress variants |
| `bilingual/language_panel/` | 60 underlying tasks in two languages, with identical candidate values |
| `bilingual/raw_records/` | 800 retained primary DeepSeek requests, responses, observations, and evaluations; English task counterparts are linked |
| `bilingual/prompt_controls/` | 3,520 original records supporting prompt engineering and execution controls, including 1,000 new checklist calls; overlaps the 800-record release |
| `data/artifacts/manifest.json` | 8,046 retained Direct/Set artifact projections in compressed JSONL shards |
| `paper/data/derived/` | Historical scored rows and per-cohort summaries; these include archived implementation controls |
| `paper/data/supplements/` | Model extensions, partial snapshots, and retained-intent evaluations |
| `paper/data/diagnostics/` | Frozen-rule replay and reference-assisted interventions |
| `paper/data/author_reports/` | Later externally supplied aggregate updates and adjudications |

The retained-intent figure cohorts contain 294 Direct/Set outcomes in four complete matched
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

## Reporting and re-scoring

The reporting scripts rebuild tables and figures from the designated inputs.
The [primary-result source note](primary_provenance.md) specifies those inputs
and their verification coverage. Cohort identifiers and source metadata select
the appropriate records for each analysis.

The requested model/configuration inventory covers 12 model identifiers and
52 model--effort settings. It describes observed request coverage, including
exploratory and partial batches, not 52 complete primary comparisons.

The [prompt engineering supplement](prompt_controls.md) compares Direct with
additional textual verification guidance on five 200-task configurations. Its
four-method panel also includes framework execution through Set (DSL) and Set-Py,
using each configuration's exact common task intersection. The offline verifier
rescores all 3,520 supporting decisions and checks that each new Prompt request
preserves the corresponding Direct input and settings apart from the checklist.

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
