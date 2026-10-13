# Archived authorization diagnostics

These studies remain part of the research record but are no longer tables or
standalone subsections in the manuscript PDF. The current narrative is about
risk-aware payment delegation: decision semantics, workflow reliability, and
whether frozen generated conditions preserve authorization beyond the current
purchase. Figure 3 and Appendix F report the prospective availability study.

## Former main-text Table 2

The component intervention study selects 16 faulty specifications from 56
Qwen/GLM outputs for **one** ambiguous ticket request, with 128- and 512-offer
catalogues. They are not 16 independent requests. Generated conditions omit
Li's reading, including refund conditions and utility binding.

| Intervention | Exact | Unsafe selection | Unsafe domain |
|---|---:|---:|---:|
| Original | 0 | 0 | 16 |
| Duplicate label | 0 | 0 | 16 |
| Reference permission | 0 | 0 | 0 |
| Reference utility | 0 | 16 | 16 |
| Both components | 16 | 0 | 0 |
| Restore omitted state | 16 | 0 | 0 |

Reference replacements are offline diagnostics. Permission correction alone
removes false admissions but leaves value errors; restoring the omitted
reading supplies both components. These observations establish a selected-case
mechanism, not an automatic repair method or a prevalence estimate.

Reporting inputs: [omitted referent records](../../paper/data/supplements/intent_ambiguity_20261011/omitted_referent.json)
and [six-condition aggregate](../../paper/data/derived/historical_oracle_ablation.json).

## Other archived studies

- The same-request input intervention contains 36 generations. Original,
  catalogue-withheld, and supplied-readings conditions have 5/12, 6/12, and
  11/12 exact decisions; overbroad domains are 6/11, 5/12, and 0/11 valid
  outputs. These cohorts are separate from both the component and availability studies.
- The historical availability probe contains 648 frozen specifications and
  1,296 paired replays. Mixed catalogues have 23 false-admitting domains and
  no unauthorized selections; unauthorized-only catalogues expose eight.
  Each condition has 12 invalid executions. Its single unsafe probe and
  coverage do not match the new prospective protocol.
- The 72-output cross-structure cohort has no utility-correction safe-to-unsafe
  transition, including two exact Qwen outputs with overbroad domains.
- The effort audit contains 1,080 outputs, 1,024 fully auditable. Greater effort
  generally improves both decisions and authorization domains. The two
  historical/strict score differences are retained separately in the archive.
- Price checks on 66 eligible recent specifications yield 16,416 valid replays
  without safe-to-unsafe reversal. In 586 archived effort specifications,
  1,392,640 ranking-only replays produce one adverse witness, for the same
  specification under generated and reference utility. Reverse transitions
  number ten and fifteen, respectively. The 10% discount is a tested step,
  not a global minimum trigger.
- The input pilot has 48 analysis units and 49 recorded semantic attempts.
  An identical-input repeat controls for generation variation. The tested
  additive value shift produces no extra false admissions or adverse switch.
- Cross-model component mixing yields 216 local combinations. Twelve utility
  substitutions improve full-catalogue value error; none changes safety to
  unsafety and two improve it. These checks do not establish a broad trend
  that better valuation increases unsafe purchasing.

The complete former supplement, including mechanisms, controls, caveats, and
primary examples, is preserved in [historical_diagnostics.tex](historical_diagnostics.tex).
The older configuration inventory is in
[historical_model_inventory.tex](historical_model_inventory.tex).
These source excerpts are archival records, not current manuscript inputs;
their old cross-references identify their original context.

## Complete follow-up record projection

[manifest.json](manifest.json) indexes 1,510 source files in
[bilingual/diagnostic_archive/followup_evidence.jsonl.gz](../../bilingual/diagnostic_archive/followup_evidence.jsonl.gz).
Each JSONL record contains the source-relative path, original source SHA-256,
publication SHA-256, and UTF-8 text. Only local account-path prefixes are
redacted. Numerical results, raw outputs, matrices, positive and negative
outcomes, exclusions, retries, and verification records are preserved. No
original experiment file was changed and no model was called for this export.
The bilingual location preserves original-language experimental content.

Historical probe data also remain in
[stress_summary.json](../../paper/data/diagnostics/stress_summary.json) and
[the earlier implementation archive](../implementation_archive/README.md).
The current availability records remain separately indexed in
[availability_20261013.md](../availability_20261013.md); cohorts are not pooled.

## Final appendix trimming

The following complete branches were also moved out of the PDF. Their reporting
inputs remain unchanged; these are scope decisions, not rescoring.

### Rule reuse and accounting

Two fixed requests each have eight catalogue snapshots. Costs include initial
compilation. Serial request seconds are summed call durations, not parallel
wall-clock latency. Reuse is valid only with fixed authorization and semantics.

| Model | Method | Calls | Input + output tokens | Serial request seconds |
|---|---|---:|---:|---:|
| Astra max | Direct | 16 | 175,429 | 344.64 |
| Astra max | Set | 2 | 22,160 | 81.69 |
| DeepSeek low | Direct | 16 | 136,345 | 351.47 |
| DeepSeek low | Set | 2 | 12,418 | 33.61 |

Both Astra routes and DeepSeek Set are exact on 16/16 snapshots; DeepSeek Direct
is exact on 15/16. The 87.4% Astra token reduction depends on the eight-catalogue
reuse schedule and two requests. It is not a general cost, latency, or reliability
claim. Source: [reuse_summary.json](../../paper/data/derived/reuse_summary.json).
The complete former subsection is in [previous_execution_controls.tex](previous_execution_controls.tex).

### Small capability checks

F01a/F02b allow a common purchase; F02a has an empty feasible intersection;
F04a tests worst-case ranking between utility pairs (3,-1) and (0.2,0.2);
F04b replaces the latter pair with (0,0), requiring refusal. Each of these five
base cases has six generations per method (three contexts, two samples).
Direct and Set each obtain 30/30. These are repeated measurements of five
constructed tasks, not a comparative advantage. The PDF retains only a short
semantic-boundary description and a recorded request-to-decision example.
The original full table and sampling description remain in
[previous_intent_ambiguity.tex](previous_intent_ambiguity.tex).

### Separate Astra 200-task language aggregates

The extra aggregate contains Chinese and English results for 200 tasks per
method, each with Direct exact/unsafe/refusal/other = 180/6/6/8 and Set =
196/2/2/0. Equal aggregate partitions do not establish identical outputs or
language invariance. These two lines were removed from the language appendix;
the complete paired 60-task panel and all its outcome partitions remain.
The primary Astra 200-task comparison is unchanged. The former language table
is [previous_language_table.tex](previous_language_table.tex); its author-reported
inputs remain in the paper's frozen data directory.

Method assumptions, formal intent experiments, Prompt guidance, output-budget
controls, and all prospective availability controls remain in the PDF. The
observed compilation examples were shortened without changing their recorded
choices or reference checks; [previous_formal_details.tex](previous_formal_details.tex)
preserves their earlier exposition.
