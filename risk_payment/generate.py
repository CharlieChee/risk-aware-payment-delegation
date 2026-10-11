"""Recreate the prospective primary benchmark from its original seeds and rules.

Only English descriptions and output paths differ from the archived generator.
No model response is consulted. The output directory must not already contain a manifest.
"""
from concurrent.futures import ProcessPoolExecutor, as_completed
from copy import deepcopy
from pathlib import Path
import argparse, hashlib, json, random
from .engine import solve, evaluate
from .run import save
from . import contracts as C, ledger as L


STRATA = [
    dict(index=0, size=128, max_affected=4, margin=1),
    dict(index=1, size=256, max_affected=4, margin=100),
    dict(index=2, size=512, max_affected=4, margin=10000),
    dict(index=3, size=1024, max_affected=4, margin=100),
    dict(index=4, size=1024, max_affected=4, margin=1),
]

MASTER_SEED = 39071007

def attributes(template, rng):
    """Independent contract attributes before boundary construction."""
    x = dict(price=rng.randrange(450000, 900001), admin=0)
    def money(lo, hi):
        return rng.randrange(lo // 100, hi // 100 + 1) * 100
    def seq(prefix, lo, hi):
        x.update({f'{prefix}_{i}': money(lo, hi) for i in range(6)})
    def groups(prefix, lo, hi):
        x.update({f'{prefix}_{j}': money(lo, hi) for j in range(3)})
    if template[0] == 'a':
        seq('loss', 500, 15000); groups('claw', 2000, 25000)
        if template == 'a2': groups('close', 500, 18000)
        if template == 'a3': x.update(group_cap=money(8000, 35000), global_claw=money(3000, 18000))
        if template == 'a4': x['rebate'] = money(5000, 38000)
        if template == 'a5': x['closure'] = money(5000, 20000)
    elif template[0] == 'b':
        seq('loss', 1000, 30000)
        if template == 'b1':
            seq('ded', 500, 18000); seq('cover', 500, 25000); x['coverage'] = money(5000, 50000)
        elif template == 'b2': x.update(deductible=money(1000, 30000), coverage=money(5000, 40000))
        elif template == 'b3': x.update(deductible=money(1000, 25000), small_cap=money(20000, 50000), large_cap=money(2000, 19000))
        elif template == 'b4': x.update(primary_ded=money(1000, 25000), primary_cap=money(5000, 25000), secondary_ded=money(0, 20000), secondary_cap=money(5000, 35000))
        elif template == 'b5': x.update(franchise=money(15000, 60000), coverage=money(15000, 65000))
    elif template[0] == 'c':
        seq('item', 50000, 140000); seq('restock', 500, 12000); seq('freight', 1000, 15000)
        subtotal = sum(x[f'item_{i}'] for i in range(6))
        if template == 'c1':
            for j in range(2):
                part = sum(x[f'item_{i}'] for i in range(j * 3, j * 3 + 3))
                x[f'threshold_{j}'] = rng.randrange(part // 3, part + 1)
                x[f'promo_{j}'] = money(3000, 18000)
            x['price'] = subtotal - x['promo_0'] - x['promo_1']
        else:
            x['promo'] = money(5000, 28000)
            if template == 'c3':
                x['low_threshold'] = rng.randrange(subtotal // 5, subtotal // 2)
                x['high_threshold'] = rng.randrange(subtotal // 2, subtotal + 1)
                x['low_promo'] = money(0, x['promo'])
            else:
                x['threshold'] = rng.randrange(subtotal // 3, subtotal + 1)
            x['price'] = subtotal - x['promo']
            if template == 'c4':
                x.update({f'weight_{i}': rng.randrange(50, 2001) for i in range(6)})
                weight = sum(x[f'weight_{i}'] for i in range(6))
                x.update(ship_subsidy=money(1000, 12000), weight_threshold=rng.randrange(weight // 3, weight + 1))
                x['price'] -= x['ship_subsidy']
            if template == 'c5':
                x.update(restock_cap=money(2000, 25000), free_return_threshold=rng.randrange(subtotal // 4, subtotal * 3 // 4 + 1))
    elif template[0] == 'd':
        seq('replacement', 1000, 30000); seq('refund', 1000, 35000)
        if template == 'd3':
            x.update(small_cap=money(20000, 60000), large_cap=money(2000, 19000))
        else:
            x['refund_cap'] = money(3000, 65000)
        if template == 'd1': seq('item_cap', 1000, 30000)
        if template == 'd2': groups('setup', 1000, 16000)
        if template == 'd4': seq('credit', 500, 30000); x['credit_cap'] = money(5000, 50000)
        if template == 'd5':
            groups('dispatch', 1000, 15000)
            x.update(bonus=money(5000, 35000), bonus_threshold=money(20000, 100000))
    assert set(x) == set(C.public_template(template, 4)['attributes'])
    assert all(type(v) is int and v >= 0 for v in x.values())
    assert L.purchase_ok(template, x)
    return x

def check_symbolic(template, public, reference, spec):
    got = solve(spec, public['candidates'])
    assert got['reason_code'] != 'invalid_spec', got.get('detail')
    for field in ('decision', 'allowed_ids', 'guaranteed_utility'):
        assert got[field] == reference[field], (template, field, got[field], reference[field])
    for left, right in zip(got['matrix'], reference['matrix']):
        assert left['id'] == right['id']
        assert left['safe'] == right['safe'] and left['psi'] == right['psi'], (template, left['id'])
    return len(got['matrix']) * len(spec['states'])

def one_pair(job):
    template, stratum, output = job
    here = Path(output)
    index = C.TEMPLATES.index(template)
    seed = MASTER_SEED + index * 100 + stratum['index']
    rng = random.Random(seed)
    public = C.public_template(template, stratum['max_affected'])
    chosen = rng.randrange(stratum['size'])
    candidates = []
    for i in range(stratum['size']):
        x = attributes(template, rng)
        worst = L.row_audit(template, x, stratum['max_affected'])['worst_loss']
        target = C.CAP - stratum['margin'] if i == chosen else C.CAP + rng.randrange(1, 20001)
        x['admin'] = target - worst
        assert x['admin'] >= 0
        cid = 'offer_' + hashlib.sha256(f'{seed}:identity:{i}'.encode()).hexdigest()[:12]
        candidates.append(dict(id=cid, attrs=x))
    public['candidates'] = candidates
    spec = C.gold_spec(template, stratum['max_affected'])
    family = C.FAMILIES[template[0]]
    pair_id = f'{template}_i{stratum["index"] + 1}'
    pair = []
    verified = 0
    for expected in ('accept', 'reject'):
        p = deepcopy(public)
        if expected == 'reject':
            p['candidates'][chosen]['attrs']['admin'] += stratum['margin'] + 1
        ref = L.reference(template, p['candidates'], stratum['max_affected'])
        assert ref['decision'] == expected
        safe = [row for row in ref['matrix'] if row['safe']]
        assert len(safe) == (1 if expected == 'accept' else 0)
        verified += check_symbolic(template, p, ref, spec)
        # Model-facing file name and content do not reveal pair membership/answer.
        identity = hashlib.sha256(f'case:{pair_id}:{expected}:{MASTER_SEED}'.encode()).hexdigest()[:18]
        cid = f'case_{identity}'
        pub = here/'public'/(cid + '.json')
        private = here/'reference'/(cid + '.json')
        meta = dict(id=cid, pair_id=pair_id, template=template, title=C.TITLES[template], family=family,
                    seed=seed, stratum=stratum, expected=expected, designated_id=candidates[chosen]['id'],
                    designated_position=chosen, public_path="public/"+pub.name, reference_path="reference/"+private.name)
        save(pub, p)
        save(private, dict(metadata=meta, reference=ref, gold_spec=spec,
                           verification=dict(independent_bitmask_ledger=True, expression_engine_agrees_on_all_rows=True)))
        pair.append(meta)
    # Verify the pair differs in exactly one scalar, without changing ordering/IDs.
    p0 = json.loads((here/pair[0]['public_path']).read_text())
    p1 = json.loads((here/pair[1]['public_path']).read_text())
    changed = p1['candidates'][chosen]['attrs']['admin'] - p0['candidates'][chosen]['attrs']['admin']
    assert changed == stratum['margin'] + 1
    p1['candidates'][chosen]['attrs']['admin'] -= changed
    assert p0 == p1
    return dict(pair_id=pair_id, cases=pair, state_candidate_checks=verified,
                pair_scalar_changes=1, pair_admin_delta=changed)

def property_audit():
    assert (C.CAP, C.PRICE_CAP, C.VALUE) == (L.LIMIT, L.BUDGET, L.BENEFIT)
    rng = random.Random(39191007)
    checks = 0
    # Check EVERY event, not just maxima, on a separate broad attribute sample.
    for template in C.TEMPLATES:
        for _ in range(20):
            x = attributes(template, rng)
            x['admin'] = rng.randrange(0, 50000)
            for mask in range(64):
                members = tuple(i for i in range(6) if mask & (1 << i))
                lhs = evaluate(C.event_loss(template, members), x)
                rhs = L.cash_loss(template, x, mask)
                assert lhs == rhs, (template, mask, lhs, rhs)
                checks += 1
    # Hand-computed threshold witnesses expose common nonmonotone/strictness errors.
    b = attributes('b5', rng)
    b.update(loss_0=20000, franchise=20000, coverage=50000, admin=0)
    assert L.cash_loss('b5', b, 1) == 20000
    assert evaluate(C.event_loss('b5', (0,)), b) == 20000
    b['loss_0'] = 20100
    assert L.cash_loss('b5', b, 1) == 0
    assert evaluate(C.event_loss('b5', (0,)), b) == 0
    c = attributes('c3', rng)
    kept_value = sum(c[f'item_{i}'] for i in range(1, 6))
    c.update(low_threshold=kept_value, high_threshold=kept_value + 1, low_promo=1000, promo=5000, restock_0=200, freight_0=300, admin=7)
    assert L.cash_loss('c3', c, 1) == 4507
    assert evaluate(C.event_loss('c3', (0,)), c) == 4507
    return dict(event_checks=checks, strict_threshold_hand_checks=3,
                constants_match=True, model_inference_calls=0)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--templates',nargs='+',default=C.TEMPLATES,choices=C.TEMPLATES)
    parser.add_argument('--strata',nargs='+',type=int,default=list(range(5)),choices=list(range(5)))
    args=parser.parse_args()
    if (args.output/'manifest.json').exists():
        parser.error('Output already has a manifest; use a fresh directory.')
    audit=property_audit()
    save(args.output/'property_audit.json',audit)
    jobs=[(t,STRATA[i],str(args.output)) for t in args.templates for i in args.strata]
    pairs=[]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for f in as_completed([pool.submit(one_pair,j) for j in jobs]):
            row=f.result();pairs.append(row)
            save(args.output/'pairs'/f"{row['pair_id']}.json",row)
            print(f"{len(pairs)}/{len(jobs)} pairs verified",flush=True)
    pairs.sort(key=lambda r:r['pair_id'])
    save(args.output/'manifest.json',dict(master_seed=MASTER_SEED,cases=[c for r in pairs for c in r['cases']],
         state_candidate_checks=sum(r['state_candidate_checks'] for r in pairs),property_audit=audit))

if __name__=='__main__':main()
