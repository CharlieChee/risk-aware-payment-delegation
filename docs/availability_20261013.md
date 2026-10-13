# Frozen specifications under changing candidate availability

This prospective diagnostic supports Figure 3 and Appendix F of
*Risk-Aware Payment Delegation: From Intent to Executable Decisions*.
It does not add a new purchase policy. It tests whether generated conditions
preserve authorization when preferred offers become unavailable.

## Design and retained cohort

Before inference, 800 request-contract inputs were frozen: 40 numerical
instances of each of 20 templates in four contract families, with 128 offers
per request. DeepSeek Flash (`deepseek-flash`), GLM (`glm-5.3`), and Qwen Max
(`qwen3.8-max`) each use low effort and a 32,768-token output budget.
Condition generation sees requests, contracts and schemas, without catalogues
or reference labels. Numerical variants and model repetitions are not new
independent logical structures.

Each fixed request-model pair contributes its first fully evaluable output,
with unchanged requests repeated when needed. Retention depends only on
complete-domain evaluability, not correctness, safety, or exposure; evaluability
does not certify semantic faithfulness. These results describe retained
specifications rather than single-attempt workflow reliability. The closed
cohort contains 2,373 evaluable outputs and 27 unresolved Qwen responses without
a terminal completion event. All attempts are indexed below.

| Model | Planned | Evaluable | Initially safe | Hidden false admission | Exposure within 8 removals |
|---|---:|---:|---:|---:|---:|
| DeepSeek Flash low | 800 | 800 | 791 | 12 (1.50%) | 12 (1.50%) |
| GLM low | 800 | 800 | 741 | 55 (6.88%) | 33 (4.13%) |
| Qwen Max low | 800 | 773 | 766 | 4 (0.50%) | 3 (0.38%) |
| All | 2,400 | 2,373 | 2,298 | 71 (2.96%) | 48 (2.00%) |

The last two columns use all 800 planned slots per model (2,400 pooled) as
their denominator, including unresolved acquisition outcomes. A numerator
requires an observed, verified event. No unobserved outcome is asserted safe.
The evaluable cohort also contains 69 initially unauthorized purchases and six
false refusals. These are mechanism-event percentages, not a single-attempt
model-reliability ranking. `publication_reporting.json` records this uniform
reporting rule and its template-cluster intervals. `summary.json` additionally
preserves the initial-safety-conditional rates used by the diagnostic engine;
those conditional rates are not the Figure 3 percentages.

For comparison, `first_attempt_summary.json` records 1,592 evaluable outputs,
1,553 initially safe purchases, 43 hidden false admissions, and 31 primary
exposures across 12 templates. These initial outputs overlap the retained
cohort reporting 48 exposures; the two counts must not be added.

## Interventions

Each specification has 146 scheduled conditions: the original catalogue,
32 random deletions each at sizes 1/4/8/16, sixteen prefixes of its original
generated ranking, and an unauthorized-only catalogue. Random plans are
frozen before model outputs and shared across models. Ranked deletion uses
generated permissions and values, with fixed original order for ties, not
reference labels. All surviving attributes, permissions, values and the
selector remain unchanged; replay makes no model calls.

The primary endpoint is an initially safe purchase becoming unauthorized at
some prefix of at most eight removals, while retaining an offer authorized
and positively valued under **both** generated and reference conditions.
All positive-value maximizers are evaluated; mixed-authorization ties and
stable-first selection are tracked separately. Cumulative exposure is not
the instantaneous outcome at exactly the budget, or a random-stockout rate.

The endpoint covers 48 requests, 15 templates, four contract families, and
three configurations. All 48 maximizing sets are wholly unauthorized; the
minimum witnesses retain 40-67 viable authorized alternatives. Eight began
with exact decisions. Cumulative exposure counts at 1/4/8/16 are 17/34/48/61.
All 71 hidden false admissions include positive-value unauthorized offers.
The full per-template distribution, reverse transitions, random controls,
and descriptive template-cluster intervals are included in `summary.json`.

Each template has 20 S and 20 T requests. S places an authorized offer first
under unrestricted reference valuation, with 1/4/8/16/24 high-value authorized
offers; T has an unauthorized offer above all authorized offers. All primary
exposures occur in S. These are deliberately constructed pressure conditions,
not a representative market sample or a deployment prevalence estimate.

## Verification and files

The independent reference preflight checks 5,836,800 candidate-event pairs.
Every observed transition and attainable minimum-deletion witness was
recomputed from the original expressions. Source hashes identify the original
local bytes; the public projection removes credentials and workstation paths.

| Path | Contents |
|---|---|
| `data/availability_20261013/summary.json` | Closed-cohort counts, coverage, controls and descriptive intervals |
| `data/availability_20261013/first_attempt_summary.json` | Separate complete initial cohort |
| `data/availability_20261013/planned_units.json` | All 2,400 slots, retained attempt, status and source hashes |
| `data/availability_20261013/attempt_index.jsonl.gz` | All 4,849 acquisition attempts and evaluability gates |
| `data/availability_20261013/witnesses.json` | All 71 hidden-domain witnesses, including non-primary cases |
| `bilingual/availability_20261013/tasks.jsonl.gz` | Frozen public task inputs, candidates, reference matrices and random plans |
| `bilingual/availability_20261013/requests.jsonl.gz` | Original generation messages and configurations, without credentials |
| `bilingual/availability_20261013/attempt_outputs.jsonl.gz` | Original answer text, parsed specifications, completion and usage receipts for every attempt |
| `bilingual/availability_20261013/retained.jsonl.gz` | Retained specifications, answer text, candidate matrices and verification receipts |
| `bilingual/availability_20261013/failures.jsonl.gz` | The 27 remaining failures, including partial outputs and completion evidence |
| `scripts/availability_20261013/` | Frozen evaluator, catalogue audit and standalone offline verification |

The bilingual directory preserves original-language text. Compressed JSONL is
a documented projection, not a byte-for-byte copy of provider event streams;
those streams remain in the local experiment archive. Attempt records are not
independent tasks.

Reconstruct all retained-slot endpoints and check every primary witness:

```bash
python scripts/availability_20261013/verify.py --native-witnesses
```

This uses the standard library and calls no model. It verifies shard hashes,
replays the 146 scheduled conditions per slot from the matrices, and evaluates
all 48 primary witnesses from the saved expressions. The resulting report is
`output/availability_20261013_verification.json`. The command reuses frozen
reference matrices; the independent reference-preflight receipt is supplied
separately and is not claimed to be rerun by this command.

The new availability evidence does not establish broad replication of the
separate selected-output utility-correction reversal. That former main-text
table and all earlier positive and negative explorations are preserved in
[the diagnostic archive](diagnostic_archive/README.md), outside the current PDF.
Figure 3 carries the primary budget, request/template/family coverage, and
planned-cohort percentage; no replacement family-summary table is added.
