"""Twenty prospective financial-contract variants. No model outputs are read.

This file describes the public task and builds a symbolic reference. The cash
ledger in ledger.py implements the financial rules separately, without using
these expressions. Amounts are exact integer monetary subunits.
"""

import itertools

CAP = 200000

PRICE_CAP = 1200000

VALUE = 2000000

PARTS = 6

PAIRS = ((0, 1), (2, 3), (4, 5))

TRIPLETS = ((0, 1, 2), (2, 3, 4), (0, 4, 5))

FAMILIES = {
    'a': 'coupon_cancellation', 'b': 'insured_cancellation',
    'c': 'threshold_returns', 'd': 'service_replacement',
}

TITLES = {'a1': 'Overlapping discount-group clawbacks', 'a2': 'Single and joint cancellation fees', 'a3': 'Capped group clawbacks with a conditional order fee', 'a4': 'Compensation for multiple broken groups', 'a5': 'Maximum group clawback with a combination surcharge', 'b1': 'Per-item deductibles and coverage with an order cap', 'b2': 'Order deductible with proportional coinsurance', 'b3': 'Coverage limit conditional on the number of cancellations', 'b4': 'Primary and residual-loss insurance', 'b5': 'First-unit coverage after a franchise threshold', 'c1': 'Separate group promotion clawbacks', 'c2': 'Maximum return freight within fixed packages', 'c3': 'Tiered retained-value discounts', 'c4': 'Value and weight thresholds for shipping subsidies', 'c5': 'Capped restocking fees and freight waivers', 'd1': 'Per-service and order-wide compensation caps', 'd2': 'Fixed activation fees for replacement groups', 'd3': 'Compensation cap conditional on the number of service failures', 'd4': 'Cash and authorized discounted service credit', 'd5': 'Group dispatch fees and threshold compensation'}

TEMPLATES = list(TITLES)

def add_terms(parts):
    parts = list(parts)
    return '(' + '+'.join(parts) + ')' if parts else '0'

def total(prefix, members):
    return add_terms(f'{prefix}_{i}' for i in members)

def maximum(parts):
    parts = list(parts)
    return f'max({",".join(parts)})' if len(parts) > 1 else parts[0] if parts else '0'

def event_loss(template, members):
    """Reference expression for one specified event, not an oracle for a model."""
    s = set(members)
    if not s:
        return '0'
    if template.startswith('a'):
        gross = total('loss', members)
        broken = [j for j, pair in enumerate(PAIRS) if len(s.intersection(pair)) == 1]
        partial = add_terms(f'claw_{j}' for j in broken)
        if template == 'a1':
            fees = add_terms(f'claw_{j}' for j, g in enumerate(TRIPLETS) if 0 < len(s.intersection(g)) < len(g))
            base = f'({gross}+{fees})'
        elif template == 'a2':
            fees = add_terms(f'claw_{j}' if len(s.intersection(g)) == 1 else f'close_{j}'
                             for j, g in enumerate(PAIRS) if s.intersection(g))
            base = f'({gross}+{fees})'
        elif template == 'a3':
            extra = 'global_claw' if len(s) >= 2 and 0 not in s else '0'
            base = f'({gross}+min(group_cap,{partial})+{extra})'
        elif template == 'a4':
            eligible = 'rebate' if len(broken) >= 2 else '0'
            base = f'({gross}+{partial}-min({partial},{eligible}))'
        elif template == 'a5':
            extra = 'closure' if {0, 5}.issubset(s) else '0'
            base = f'({gross}+{maximum(f"claw_{j}" for j in broken)}+{extra})'
        else:
            raise ValueError(template)
    elif template.startswith('b'):
        gross = total('loss', members)
        if template == 'b1':
            item_pay = add_terms(f'min(cover_{i},max(0,loss_{i}-ded_{i}))' for i in members)
            pay = f'min(coverage,{item_pay})'
        elif template == 'b2':
            pay = f'min(coverage,max(0,{gross}-deductible)/2)'
        elif template == 'b3':
            cap = 'small_cap' if len(s) <= 2 else 'large_cap'
            pay = f'min({cap},max(0,{gross}-deductible))'
        elif template == 'b4':
            primary = f'min(primary_cap,max(0,{gross}-primary_ded))'
            secondary = f'min(secondary_cap,max(0,{gross}-{primary}-secondary_ded))'
            pay = f'({primary}+{secondary})'
        elif template == 'b5':
            pay = f'(min(coverage,{gross}) if {gross}>franchise else 0)'
        else:
            raise ValueError(template)
        base = f'({gross}-{pay})'
    elif template.startswith('c'):
        kept = [i for i in range(PARTS) if i not in s]
        remain = total('item', kept)
        restock = total('restock', members)
        freight = maximum(f'freight_{i}' for i in members)
        if template == 'c1':
            claw = add_terms(f'(promo_{j} if {total("item", [i for i in g if i not in s])}<threshold_{j} else 0)'
                             for j, g in enumerate(((0, 1, 2), (3, 4, 5))))
        elif template == 'c2':
            freight = add_terms(maximum(f'freight_{i}' for i in g if i in s) for g in PAIRS)
            claw = f'(promo if {remain}<threshold else 0)'
        elif template == 'c3':
            entitlement = f'(promo if {remain}>=high_threshold else (low_promo if {remain}>=low_threshold else 0))'
            claw = f'(promo-{entitlement})'
        elif template == 'c4':
            weight = total('weight', kept)
            claw = f'((promo if {remain}<threshold else 0)+(ship_subsidy if {weight}<weight_threshold else 0))'
        elif template == 'c5':
            restock = f'min(restock_cap,{restock})'
            freight = f'(0 if {total("item", members)}>=free_return_threshold else {freight})'
            claw = f'(promo if {remain}<threshold else 0)'
        else:
            raise ValueError(template)
        base = f'({restock}+{freight}+{claw})'
    elif template.startswith('d'):
        bill = total('replacement', members)
        nominal = total('refund', members)
        if template == 'd1':
            pay = f'min(refund_cap,{add_terms(f"min(refund_{i},item_cap_{i})" for i in members)})'
        elif template == 'd2':
            bill = f'({bill}+{add_terms(f"setup_{j}" for j, g in enumerate(PAIRS) if s.intersection(g))})'
            pay = f'min(refund_cap,{nominal})'
        elif template == 'd3':
            cap = 'small_cap' if len(s) <= 2 else 'large_cap'
            pay = f'min({cap},{nominal})'
        elif template == 'd4':
            cash = f'min(refund_cap,{nominal})'
            credit = f'min(credit_cap,{total("credit", members)})/2'
            pay = f'({cash}+{credit})'
        elif template == 'd5':
            bill = f'({bill}+{add_terms(f"dispatch_{j}" for j, g in enumerate(TRIPLETS) if s.intersection(g))})'
            bonus = f'(bonus if {total("replacement", members)}>=bonus_threshold else 0)'
            pay = f'(min(refund_cap,{nominal})+{bonus})'
        else:
            raise ValueError(template)
        base = f'max(0,{bill}-{pay})'
    else:
        raise ValueError(template)
    return f'({base}+admin)'

def price_contract(template):
    """Initial purchase eligibility, including exactly stated promotion identities."""
    hard = f'price <= {PRICE_CAP}'
    if template[0] != 'c':
        return hard
    subtotal = total('item', range(PARTS))
    if template == 'c1':
        extra = f'price == {subtotal}-promo_0-promo_1'
        for j, g in enumerate(((0, 1, 2), (3, 4, 5))):
            extra += f' and {total("item", g)} >= threshold_{j}'
    else:
        discounts = 'promo+ship_subsidy' if template == 'c4' else 'promo'
        threshold = 'high_threshold' if template == 'c3' else 'threshold'
        extra = f'price == {subtotal}-({discounts}) and {subtotal}>={threshold}'
        if template == 'c4':
            extra += f' and {total("weight", range(PARTS))}>=weight_threshold'
    return hard + ' and ' + extra

def expression_events(max_affected):
    return [x for k in range(max_affected + 1) for x in itertools.combinations(range(PARTS), k)]

def gold_spec(template, max_affected):
    states = []
    for event in expression_events(max_affected):
        loss = event_loss(template, event)
        states.append(dict(label='event_' + ('_'.join(map(str, event)) if event else 'none'),
                           hard=price_contract(template), risk=f'{loss}<={CAP}',
                           utility=f'{VALUE}-price-{loss}'))
    return dict(states=states, reject_utility='0', catalog_complete=True,
                source_ids=['U-task', 'U-events', 'U-contract', 'U-budget', 'U-utility'])


def public_template(template, max_affected):
    """Published English task template; the primary generator uses four affected components."""
    from pathlib import Path
    import json
    if max_affected != 4:
        raise ValueError('Published natural-language templates specify max_affected=4.')
    return json.loads((Path(__file__).resolve().parents[1]/'benchmarks/primary/templates.json').read_text())[template]
