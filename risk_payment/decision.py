"""Complete-catalogue decision contract from Algorithm 1.

The historical evaluator is retained unchanged in engine.py. This wrapper
certifies optimum/refusal only when all relevant evidence is resolved.
"""
from fractions import Fraction
from .engine import solve


def decide(spec, candidates, catalogue_complete=True):
    model = dict(spec, reject_utility='0', catalog_complete=catalogue_complete)
    result = solve(model, candidates)
    if result['reason_code'] == 'invalid_spec':
        return dict(status='failure', reason='invalid_spec', detail=result['detail'],
                    allowed_ids=[], guaranteed_utility=None)
    if not catalogue_complete:
        return dict(status='failure', reason='uncertified_catalogue', allowed_ids=[], guaranteed_utility=None)
    feasible = []
    for row in result['matrix']:
        if row['proven_unsafe']:
            continue
        if not row['safe'] or row['psi'] is None:
            return dict(status='failure', reason='unresolved_relevant_evidence',
                        allowed_ids=[], guaranteed_utility=None)
        feasible.append((row['id'], Fraction(row['psi'])))
    if not feasible:
        return dict(status='refuse', reason='infeasible', allowed_ids=[], guaranteed_utility=None)
    best = max(v for _, v in feasible)
    if best <= 0:
        return dict(status='refuse', reason='nonpositive_value', allowed_ids=[], guaranteed_utility=None)
    return dict(status='accept', reason='optimal',
                allowed_ids=[i for i, v in feasible if v == best], guaranteed_utility=str(best))


def score(output, reference):
    """One mutually exclusive outcome per task; failures stay in the denominator."""
    base = dict(exact=False, unsafe=False, false_refusal=False, other=False)
    try:
        decision = output['decision']
        ids = output['allowed_ids']
        if decision not in ('accept', 'reject') or not isinstance(ids, list):
            raise ValueError('invalid decision')
        if any(not isinstance(i, str) for i in ids) or len(set(ids)) != len(ids):
            raise ValueError('invalid candidate identifiers')
        value = output['guaranteed_utility']
        if decision == 'reject':
            if ids or value is not None:
                raise ValueError('invalid refusal')
            category = 'exact' if reference['decision'] == 'reject' else 'false_refusal'
        else:
            if not ids or not isinstance(value, str):
                raise ValueError('invalid acceptance')
            matrix = {r['id']: r for r in reference['matrix']}
            if any(i not in matrix for i in ids):
                raise ValueError('unknown candidate')
            if any(not matrix[i]['safe'] for i in ids):
                category = 'unsafe'
            elif (set(ids).issubset(reference['allowed_ids']) and
                  reference['guaranteed_utility'] is not None and
                  Fraction(value) == Fraction(reference['guaranteed_utility'])):
                category = 'exact'
            else:
                category = 'other'
    except (ValueError, TypeError, KeyError, ZeroDivisionError):
        category = 'other'
    return dict(base, **{category: True}, category=category)
