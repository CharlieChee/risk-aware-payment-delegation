# Experimental protocol

## Decision problem

A request and its context induce retained interpretations or contractual events.
One purchase must meet every retained state's hard conditions and authorized
risk conditions. Among admissible candidates, its value is the minimum of the
state-dependent utility values. The decision selects a maximizer only when the
maximum is positive; otherwise it refuses. Tied maximizers are permitted.

The semantic front end instantiates the DSL; the interpreter's syntax and
aggregation rules are fixed. JSON is the current serialization, not the source
of the domain semantics. A generated, executable specification may still
misrepresent user requirements. Offline reference checks evaluate that distinct
source of error.

## Primary cohort

The 200 tasks comprise 20 templates and five paired numerical strata per
template. Each pair changes one administrative-fee scalar to move a designated
candidate across an authorization boundary. Four contract families cover
discount clawbacks, insurance, threshold returns, and service replacement.
Catalogues contain 128--1,024 candidates. Six components and at most four
affected components yield 57 contractual events. Each task has exactly one
admissible positive-value purchase or none.

Amounts use integer monetary subunits, with 100 subunits per MU. Identifiers
containing `cent` are historical schema names and retain their numerical scale.
The independent ledger does not call the DSL builder or interpreter. Agreement
of these implementations checks computation; it does not establish unrestricted
natural-language semantic fidelity.

## Methods and input visibility

Both Direct and Set receive the same outer decision policy. Direct receives the
catalogue and returns a decision and guaranteed utility. Set compiles the
request and attribute schema without catalogue entries; the evaluator subsequently
checks the candidates. References and scoring information are never included in
model requests. This is a comparison of complete execution architectures, not
an equal-input representation-only comparison. Matched-input execution controls
are retained with their own cohort labels.

Historical retained-intent experiments used catalogue-visible input and explicitly
retained the relevant alternatives. Their protocol differs from primary
catalogue-independent compilation. They should not be described as a test of
automatic discovery of every possible ambiguity.

## Metrics and reporting

Exact decisions require a correct purchase or justified refusal and, for a
purchase, correct guaranteed utility. Unsafe acceptance, false refusal, and
other errors are mutually exclusive reporting categories. Invalid output and
operational failures remain in denominators. Safe completion is measured over
feasible tasks; unsafe acceptance uses the full designated cohort.

Bootstrap intervals preserve paired tasks and cluster by contract template.
Different model configurations, reruns, diagnostics, and language conditions
are separate cohorts. Requested reasoning settings are not equal-compute
budgets. The configuration inventory records historical request metadata and
the source of subsequently reported cap metadata; it does not assert that a
provider accepted or consumed its maximum on every call.

## Historical and current execution contracts

`engine.py` is the retained experiment interpreter. It optimizes over certified
observed candidates. `decision.py` adds the manuscript's complete-catalogue
certification condition: unresolved eligibility or utility that could affect
optimality yields a separate failure. A known false requirement makes a
candidate ineligible, so its unknown utility is irrelevant. The two contracts
agree on the fully specified reference inputs in the primary benchmark.
Historical scores are not rewritten by the wrapper.
