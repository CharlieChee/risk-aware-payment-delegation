# Reproduction guide

## Offline reporting

Run `python reproduce.py`. Inputs in `paper/data/` are hash-checked before and
after reporting. The entry runs tests, rebuilds tables and figures, verifies
Figure 3's four paired outcome partitions, and checks Algorithm 1. It makes no
model calls. `--pdf` adds LaTeX compilation. The source can also be compiled with
`latexmk -pdf paper.tex` from `paper/`.

The exact plotting values are stored beside the figures. The manuscript's
LaTeX is editable in `paper/paper.tex`, `paper/evaluation.tex`, and
`paper/sections/`; an inlined source is supplied as `paper/paper_all_in_one.tex`.

## Reference verification and regeneration

```bash
python -m risk_payment.verify --workers 4
python -m risk_payment.generate --output output/regenerated --workers 4
```

The first command checks all 200 frozen cases, every candidate's permission and
guaranteed utility, feasibility pairing, and bilingual numeric consistency.
The second regenerates the primary distribution from the original seeds,
validates the financial formulas against the independent ledger, and writes a
new dataset. It never overwrites the released benchmark. English request
descriptions come from the reviewed translation assets. For a quick generator
check, add `--templates a1 --strata 0`.

`data/validation/` retains the release checks. Elapsed times describe the local
verification machine; they are not model inference times.

## New inference runs and interruption recovery

The runner requires an HTTPS OpenAI-compatible chat endpoint. Model identifiers
are passed through; the repository's historical identifiers do not guarantee
availability from another provider. Concurrency and output caps are explicit
command-line settings. The default output cap is 32,768 tokens. JSON mode and
reasoning effort are optional because support varies by endpoint.

Each case directory contains:

1. `request.json`: public model payload, protocol version, and configuration hash.
2. `response.json`: the completed response, usage, and request duration, saved
   immediately after the call returns.
3. `result.json`: parsed output, execution outcome, and reference-based score.

Repeated invocation reuses completed responses even if the process stopped
before scoring. A run-directory lock prevents two local runners from sending
the same batch concurrently. A network interruption before a response reaches
the client can still leave a provider-side charge without a local response;
the runner cannot guarantee recovery of a response the service never delivered.
No automatic retries conceal such failures. To conduct a separate rerun, choose
a new output directory and keep both runs.

References are loaded only after response recording and model-output execution.
An `other` outcome includes malformed output, unresolved execution, and
operational failures. A runner failure is never recoded as a correct refusal.

The runtime and inference harness use the standard library. NumPy and Matplotlib
are needed for paper statistics and figures, and pypdf for manuscript checks.
The optional runner is supported on Linux and macOS; no operating-system-specific
CLI model installation is required.
