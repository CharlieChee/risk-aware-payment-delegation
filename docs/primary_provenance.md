# Primary-result inputs

`paper/scripts/primary_profiles.py::display_primary` selects the inputs for the
eleven primary configurations. The [source map](../paper/reporting_checks/review_revision_evidence.json)
records each configuration, method, and input path.

GLM high, Astra max, Sol medium, and Opus medium use supplied updates in
`paper/data/author_reports/20261011_confirmed_aggregates.json` and
`paper/data/author_reports/20261011_primary200_completion.json`. These support
aggregate reconstruction and arithmetic checks. Replacement raw responses are
not included in this release, so these updates do not support case-level
rescoring or paired analysis. The other configurations use archived trial
outcomes. DeepSeek template counts and paired statistics use retained trials.

The [reproduction guide](reproduction.md) provides verification commands;
the [evidence map](evidence_map.md) indexes the other experiments.
