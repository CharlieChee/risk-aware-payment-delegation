# Risk-Aware Payment Delegation

**From Intent to Executable Decisions**

A study of whether executable purchasing conditions preserve the user's
natural-language authorization, and how permission errors affect selection.
SET makes the risk-aware purchase-or-refusal policy executable and its admitted
domain inspectable. Workflow comparisons measure useful decision-making;
reference-domain checks and frozen-specification tests connect false permissions
to unauthorized purchases under changed availability. The study retains viable
authorized alternatives and verifies the exposed errors in the original
expressions. No payment is executed by this artifact.

[Anonymous artifact](https://anonymous.4open.science/r/risk-aware-payment-delegation-D4FC/) · [Read the paper](paper/paper.pdf) · [Experimental protocol](docs/protocol.md) ·
[Data guide](docs/data.md) · [Reproduction guide](docs/reproduction.md) ·
[Prompt engineering controls](docs/prompt_controls.md) ·
[Availability study](docs/availability_20261013.md) ·
[Archived diagnostic studies](docs/diagnostic_archive/README.md)

The October 13 availability study freezes generated decision conditions and
changes only which offers remain available. Its bounded-removal endpoint
exposes unauthorized purchases in 48 requests across 15 contract templates,
while viable authorized alternatives remain. Figure 3 reports percentages over
the planned cohort of 800 requests per model. The linked study protocol defines
the retained cohort and indexes the complete generation and evaluation records.

```bash
python scripts/availability_20261013/verify.py --native-witnesses
```

This additional offline check reconstructs all retained-slot catalogue tests
and re-evaluates all 48 primary witnesses from their original expressions.
It makes no model calls. See the linked study protocol for retention rules,
reference construction, controls, and the scope of the released raw projection.

## Reproduce the results

Python 3.11 or later is recommended. No API key is needed for offline reproduction.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python reproduce.py
```

This runs decision and checkpoint tests, rebuilds reporting tables and the four
figures (three in the main text and one in Appendix E), checks the retained primary request/response records, independently
rescores 3,520 supporting records for the prompt engineering and four-method
controls, and verifies the paired retained-intent outcomes. Results are written
to `paper/output/reproduction/report.json`.

To recompute **all 200 reference decisions** with the exact DSL interpreter and
the independently implemented cash-flow ledger, and to compile the paper:

```bash
python reproduce.py --verify-references --workers 4 --pdf
```

The PDF step requires `latexmk` and a TeX installation with the ACL dependencies.
The rebuilt document is `paper/output/reproduction/latex/paper.pdf`. Reference
verification performs 6,712,320 candidate-state comparisons, checks 100
feasibility pairs, and verifies 60 Chinese/English input pairs.

## What is included

| Component | Contents |
|---|---|
| `risk_payment/` | Exact expression interpreter, decision procedure, separate financial ledger, seeded task generator, English prompts, resumable API runner |
| `benchmarks/primary/` | 200 English tasks, 20 contract structures, 100 feasibility pairs, candidates, reference decisions, and symbolic specifications |
| `benchmarks/intent/` | 66 translated intent-task variants, including the 42-variant API panel and 24 stress variants; reference states and outcomes |
| `bilingual/` | 60 original Chinese/English task pairs, translation audits, the original 800-record release, and a 3,520-record prompt/control archive including 1,000 new calls |
| `data/artifacts/` | 8,046 archived Direct/Set parsed-output projections with per-record source hashes, usage, and scored outcomes |
| `paper/data/` | Retained per-trial reporting data, diagnostics, controls, and separately identified aggregate updates |
| `paper/` | Editable LaTeX, references, figure sources, plotting code, result tables, and PDF |
| `tests/` | Exact boundaries, unresolved evidence, joint decisions, failure classification, and interrupted-run recovery |

These cohorts overlap. Their sizes must not be added as independent task counts.
The requested model identifiers and settings are recorded in
[`data/configuration_inventory.json`](data/configuration_inventory.json).

## Run a new model experiment

The API runner supports OpenAI-compatible chat endpoints. It reads credentials
from environment variables and never writes them to requests or results.

```bash
export PAYMENT_API_BASE_URL="https://your-provider.example/v1"
export PAYMENT_API_KEY="your-api-key"

# Inspect the exact English requests without making API calls.
python -m risk_payment.run --model YOUR_MODEL --method set \
  --limit 2 --output runs/preview --dry-run

# A complete 200-task run. This command uses the configured paid API.
python -m risk_payment.run --model YOUR_MODEL --method set \
  --limit 200 --concurrency 4 --output-cap 32768 --output runs/model-set

# Use a separate directory for the direct-answer control.
python -m risk_payment.run --model YOUR_MODEL --method direct \
  --limit 200 --concurrency 4 --output-cap 32768 --output runs/model-direct
```

Run the same command again to resume. Requests, completed responses, execution
results, usage, and progress are saved separately. Existing responses are reused;
changing a request configuration requires a new output directory. Add `--effort`
only if the endpoint supports `reasoning_effort`. Failed calls remain scored as
failures; there is no silent retry or replacement by a more favorable answer.

## Using the released data

The repository provides the implementation, benchmark inputs and references,
prompts, model configurations, evaluation records, and frozen reporting inputs.
It includes original request/response records from the primary DeepSeek cohorts,
a 3,520-record prompt/control archive, and 8,046 archived parsed-output records. These overlapping
collections support response-level inspection; separately identified aggregate
inputs support reconstruction of the corresponding tables and figures. English
release translations are provided for inspection and new runs. See the
[data guide](docs/data.md) for cohort definitions, source mappings, and the
distinction between reporting and re-scoring.

The complete-catalogue decision procedure reports unresolved relevant evidence
as a failure, not as a certified optimum or justified refusal. Its guarantees are
conditional on the represented semantics. The framework adopts RAC's fixed-set
decision principle; it does not implement conformal calibration.

## Citation and license

Use [`CITATION.cff`](CITATION.cff) or cite the accompanying manuscript. Original
code and synthetic data are available under the MIT license. Third-party ACL
formatting files retain their own notices; see [NOTICE](NOTICE).

The [result-to-evidence map](docs/evidence_map.md) links the manuscript's claims,
cohorts, retained responses, and offline verification commands.

Implementation controls and their original provenance are indexed in
[the code supplement](docs/implementation_archive/README.md). The manuscript
retains the original primary Set cohort. Figure 3 and Appendix F report the
prospective availability study; earlier component, input, price, and catalogue
explorations remain in [the diagnostic archive](docs/diagnostic_archive/README.md),
with their full controls and non-triggering results.
