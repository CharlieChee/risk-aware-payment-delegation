# Risk-Aware Payment Delegation

**From Intent to Executable Decisions**

An executable research framework for purchasing decisions when the user cannot
provide further clarification. A state-wise intent DSL retains relevant
interpretations and contractual events. A fixed evaluator checks joint
admissibility, compares worst-case utility, and selects a positive-value purchase
or refuses. No payment is executed by this artifact.

[Anonymous artifact](https://anonymous.4open.science/r/risk-aware-payment-delegation-D4FC/) · [Read the paper](paper/paper.pdf) · [Experimental protocol](docs/protocol.md) ·
[Data guide](docs/data.md) · [Reproduction guide](docs/reproduction.md) ·
[Prompt engineering controls](docs/prompt_controls.md)

## Reproduce the results

Python 3.11 or later is recommended. No API key is needed for offline reproduction.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python reproduce.py
```

This runs decision and checkpoint tests, rebuilds reporting tables and the four
main figures, checks the retained primary request/response records, independently
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
