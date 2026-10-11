# Prompt engineering and execution controls

This supplement adds 1,000 completed model calls: 200 tasks each for DeepSeek
Flash low/high and GPT-5.6 Sol/Luna/Terra medium. Each receives its original
Direct request plus a generic verification checklist. This additional textual
guidance is a prompt engineering baseline, abbreviated **Prompt** below. The catalogue, output
schema, model identifier, requested effort, and deadline are unchanged within
each comparison. The original Direct instruction already includes the common
feasibility, worst-case utility, and refusal policy.

## Four methods

| Method | Generated object | Decision execution |
|---|---|---|
| Direct | Purchase or refusal with a utility claim | Model answers directly |
| Prompt engineering (Prompt) | Same final answer, with an additional verification checklist | Model answers directly |
| Framework + Set | State-wise hard conditions, risk conditions, and utility | Fixed evaluator checks all states and ranks candidates |
| Framework + Python | An `assess(attrs)` function | Generated function executes under the same outer decision policy |

Direct, Prompt, and the visible-catalogue Python control see the catalogue.
Set compiles without it. These are architecture controls; input length and
execution are not held equal across all four methods. Prompt versus Direct
changes only the system suffix in the recorded requests, but calls are from
different dates and server-version drift is not controlled.

## Cohorts

- Full prompt comparison: five configurations, 200 tasks per method and
  configuration. All 1,000 new calls are included, including failures.
- Four-method comparison: DeepSeek low/high each use all 200 primary tasks.
  Sol/Luna/Terra medium each use the 40 primary tasks shared with the earlier
  Python control. This fixed subset contains one feasible/infeasible pair per
  contract template. Its membership was defined in the earlier effort study
  without consulting model outcomes. Public tasks and reference decisions
  match exactly under the stored case mapping.

The four-method panel contains 2,080 method outcomes on overlapping cohorts;
it does not add 2,080 independent tasks. Its 3,520 supporting records include
all 1,000 new Prompt calls and the retained primary comparison runs. Some
records overlap the earlier raw release. Paired controls use the archived
per-trial runs, separately from subsequent primary aggregate updates.

## Prompt variants and budgets

DeepSeek uses checklist v1. Sol/Luna/Terra use v2: the same five verification
steps, with the final prohibition on functions, expression specifications,
and pseudocode removed. Both retain the final-answer interface and provide
no tools or further user interaction. Thus these configurations do not form
a controlled comparison of checklist versions. English translations are in
`docs/prompts/`; exact measured Chinese suffixes and requests are in
`bilingual/prompt_controls/`. Translation is documentation, not a new run.

DeepSeek requests retain a 262,144 output-token cap and a 1,800-second deadline.
The native CLI runs retain the same deadline and a provider-controlled output
budget; generic API cap fields in request records are not forwarded to the
native CLI. Each call starts a fresh isolated context. Completed answers are
never retried based on correctness. Interrupted transport recovery is
checkpointed separately from decision scoring.

## Inspect and reproduce

`bilingual/prompt_controls/manifest.json` indexes compressed original requests,
observations, provider responses or native event streams, and evaluations.
Only workstation metadata is anonymized; measured prompts and final response
text are preserved. Source hashes accompany every record.

The English numerical projection in
`paper/data/supplements/prompt_controls_20261011/rows.json` supplies the table
builder. `cohorts.json` defines the exact four-method task intersection.

```bash
python scripts/verify_prompt_controls.py
python paper/scripts/prompt_control_reporting.py
```

The first command checks archive hashes, preserves actual denominators,
verifies all 1,000 prompt-only input changes, and independently rescores the
3,520 captured final decisions against the released reference matrices. It
does not regenerate model responses or execute archived Python programs.
The second rebuilds both appendix tables and their summary JSON without
calling a model. Both checks are also part of `python reproduce.py`.

## Observed results

All rows use 200 tasks per method. The reported quantities are exact-decision
percentages; the change is Prompt minus Direct in percentage points.

| Configuration | Direct | Prompt engineering | Change |
|---|---:|---:|---:|
| DeepSeek low | 58.5 | 53.5 | -5.0 |
| DeepSeek high | 65.5 | 59.0 | -6.5 |
| Sol medium | 68.5 | 67.5 | -1.0 |
| Luna medium | 20.5 | 19.0 | -1.5 |
| Terra medium | 40.5 | 41.5 | +1.0 |

The comparison tests whether additional textual reasoning and verification
guidance can substitute for executable decision processing. This particular
prompt engineering intervention does not consistently improve exact decisions.
Both the Direct baseline and the executable framework also use prompts; the
contrast is not prompting versus no prompting. It does not establish that
prompt engineering as a whole is ineffective, or that either executable
representation is uniformly best.
