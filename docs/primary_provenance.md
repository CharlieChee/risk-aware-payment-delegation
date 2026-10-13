# Primary-result sources and verification

The primary comparison has eleven configurations and 200 tasks per method.
`paper/scripts/primary_profiles.py::display_primary` selects each reporting input.
The [machine-readable source map](../paper/reporting_checks/review_revision_evidence.json)
records the configuration, arm, input path, and available evidence.

Seven configurations use archived per-trial outcomes, with complete-domain
rescoring where applicable. GLM high, Astra max, Sol medium, and Opus medium use
the supplied aggregate updates in these two files:

- `paper/data/author_reports/20261011_confirmed_aggregates.json`: GLM, Astra, and Sol updates.
- `paper/data/author_reports/20261011_primary200_completion.json`: completed error partitions and useful-completion counts, including the completed Opus comparison that supersedes its earlier partial display.

The original replacement responses have not yet been imported. These inputs
support reconstruction of the displayed aggregates and arithmetic checks;
case-level rescoring, pairing, template counts, and usage cannot be recovered
from the aggregates alone. Sol Direct's supplied counts also agree with the
retained local observations. Earlier local runs remain separately archived.
Paired statistics use retained observations, including the DeepSeek records
used for the primary template-bootstrap analysis.

The [evidence map](evidence_map.md) indexes the remaining results. Report
reconstruction, rescoring a retained response, and recomputing a benchmark
reference are separate checks; the [reproduction guide](reproduction.md)
provides their commands and coverage. None requires new model calls.
