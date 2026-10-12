"""Verify the observed primary contract trace without model calls.

The retained generated expression is checked against the compact notation in
the paper and an enumerated 57-event ledger for all 256 catalogue candidates.
"""
from pathlib import Path
from fractions import Fraction
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
ENGINE_ROOT = next(path for path in
                   (ROOT, ROOT.parent, ROOT.parent / 'risk-aware-payment-delegation')
                   if (path / 'risk_payment').is_dir())
sys.path.insert(0, str(ENGINE_ROOT))
from risk_payment.engine import evaluate
from risk_payment.decision import decide


def main():
    source = ROOT / 'data/supplements/primary_trace_20261011/trace.json'
    trace = json.loads(source.read_text())
    assert trace['source']['catalogue_visible_at_compilation'] is False
    assert 'candidates' not in trace['source']['request_keys']
    spec, candidates = trace['spec'], trace['public']['candidates']
    assert len(spec['states']) == 1 and len(candidates) == 256
    state = spec['states'][0]
    refs = {r['id']: r for r in trace['reference']['matrix']}
    checks = 0
    for c in candidates:
        a = c['attrs']
        losses = [a['loss_' + str(i)] for i in range(6)]
        g4 = sum(sorted(losses)[-4:])
        payout = min(a['coverage'], max(Fraction(0), Fraction(g4-a['deductible'], 2)))
        loss = g4-payout+a['admin']
        ledger = []
        for mask in range(64):
            if mask.bit_count() > 4:
                continue
            gross = sum(losses[i] for i in range(6) if mask & (1 << i))
            paid = min(a['coverage'], max(Fraction(0), Fraction(gross-a['deductible'], 2)))
            ledger.append(gross-paid+a['admin'] if mask else Fraction(0))
        assert len(ledger) == 57 and max(ledger) == loss
        hard, risk = a['price'] <= 1200000, loss <= 200000
        utility = 2000000-a['price']-loss
        assert evaluate(state['hard'], a) == hard
        assert evaluate(state['risk'], a) == risk
        assert evaluate(state['utility'], a) == utility
        assert refs[c['id']]['safe'] == (hard and risk)
        assert Fraction(refs[c['id']]['psi']) == utility
        assert Fraction(refs[c['id']]['worst_loss']) == loss
        checks += len(ledger)
    decision = decide(spec, candidates, catalogue_complete=True)
    observed = trace['observed_output']
    assert decision['status'] == 'accept'
    assert decision['allowed_ids'] == observed['allowed_ids']
    assert Fraction(decision['guaranteed_utility']) == Fraction(observed['guaranteed_utility'])
    selected = refs[decision['allowed_ids'][0]]
    report = dict(status='passed', model_calls=0, candidates=len(candidates),
                  event_candidate_checks=checks, generated_states=len(spec['states']),
                  source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                  compact_notation_equivalent_on_all_candidates=True,
                  complete_domain_decision=decision,
                  displayed_loss_mu=str(Fraction(selected['worst_loss'],100)),
                  displayed_value_mu=str(Fraction(selected['psi'])/100))
    (ROOT / 'output').mkdir(exist_ok=True)
    (ROOT / 'output/primary_trace_check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
