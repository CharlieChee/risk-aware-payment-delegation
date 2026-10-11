"""Check the manuscript's finite, fully certified decision contract.

This is a local reference check over evaluated matrices, not a replacement for
the historical experiment executor and not a new model experiment.
"""
from fractions import Fraction
from pathlib import Path
import json


def decide_matrix(matrix, catalogue_complete=True):
    if not catalogue_complete:
        return dict(status='fail', reason='uncertified', allowed_ids=[])
    feasible = []
    for candidate in matrix:
        states = candidate['states']
        if not states:
            return dict(status='fail', reason='execution', allowed_ids=[])
        predicates = [s[k] for s in states for k in ('hard', 'risk')]
        if any(v is not None and type(v) is not bool for v in predicates):
            return dict(status='fail', reason='execution', allowed_ids=[])
        # A known false conjunct proves ineligibility; its utility is irrelevant.
        if any(v is False for v in predicates):
            continue
        if any(v is None for v in predicates) or any(s['utility'] is None for s in states):
            return dict(status='fail', reason='uncertified', allowed_ids=[])
        values = [Fraction(s['utility']) for s in states]
        feasible.append((candidate['id'], min(values)))
    if not feasible:
        return dict(status='refuse', reason='infeasible', allowed_ids=[])
    best = max(value for _, value in feasible)
    if best <= 0:
        return dict(status='refuse', reason='nonpositive_value', allowed_ids=[])
    return dict(status='accept', allowed_ids=[i for i, v in feasible if v == best],
                guaranteed_utility=str(best))


def candidate(identity, values, hard=True, risk=True):
    return dict(id=identity, states=[dict(hard=hard, risk=risk, utility=v) for v in values])


def main():
    cases = [
        ('known_10_and_unknown', [candidate('A', [10]), candidate('B', [None])],
         True, 'fail', []),
        ('unresolved_admissibility', [candidate('A', [10]), candidate('B', [100], hard=None)],
         True, 'fail', []),
        ('resolved_better_candidate', [candidate('A', [10]), candidate('B', [100])],
         True, 'accept', ['B']),
        ('all_positive_ties', [candidate('A', [10]), candidate('B', [10])],
         True, 'accept', ['A', 'B']),
        ('nonpositive_maximum', [candidate('A', [-1]), candidate('B', [0])],
         True, 'refuse', []),
        ('proven_infeasible_unknown_utility', [candidate('B', [None], hard=False)],
         True, 'refuse', []),
        ('irrelevant_unknowns', [candidate('A', [10]), candidate('B', [None], hard=False, risk=None)],
         True, 'accept', ['A']),
        ('incomplete_catalogue', [candidate('A', [10])], False, 'fail', []),
        ('empty_complete_catalogue', [], True, 'refuse', []),
        ('state_wise_minimum', [candidate('A', [100, 1]), candidate('B', [10, 10])],
         True, 'accept', ['B']),
    ]
    checks = []
    for name, matrix, complete, status, ids in cases:
        result = decide_matrix(matrix, complete)
        assert result['status'] == status and result['allowed_ids'] == ids, (name, result)
        checks.append(dict(name=name, matrix=matrix, catalogue_complete=complete,
                           result=result, expected_status=status, expected_ids=ids))
    root = Path(__file__).resolve().parents[1]
    (root/'output').mkdir(exist_ok=True)
    report = dict(status='passed', cases=len(checks), model_calls=0,
                  scope='Reference checks of the revised manuscript contract; historical records unchanged.',
                  checks=checks)
    (root/'output/algorithm_contract_check.json').write_text(json.dumps(report, indent=2)+'\n')
    print(f'{len(checks)} decision-contract checks passed; no model calls')


if __name__ == '__main__':
    main()
