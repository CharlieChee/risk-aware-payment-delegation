"""Independent exact cash-flow oracle, with bit-mask event enumeration.

Does not import the DSL builder or solver, and never reads model answers.
The duplicated monetary constants are asserted equal by the preflight audit.
"""
from fractions import Fraction

LIMIT = 200000
BUDGET = 1200000
BENEFIT = 2000000


def nonnegative(value):
    return value if value > 0 else 0


def capped(value, limit):
    return limit if value > limit else value


def cash_loss(template, x, mask):
    flags = [(mask >> i) & 1 for i in range(6)]
    affected = [i for i, flag in enumerate(flags) if flag]
    count = len(affected)
    if not count:
        return 0
    if template[0] == 'a':
        personal = sum(x['loss_' + str(i)] for i in affected)
        pair_counts = [flags[0] + flags[1], flags[2] + flags[3], flags[4] + flags[5]]
        fees = 0
        if template == 'a1':
            memberships = [[0, 1, 2], [2, 3, 4], [0, 4, 5]]
            for j, group in enumerate(memberships):
                n = sum(flags[i] for i in group)
                if n == 1 or n == 2:
                    fees += x['claw_' + str(j)]
        elif template == 'a2':
            for j, n in enumerate(pair_counts):
                if n == 1:
                    fees += x['claw_' + str(j)]
                elif n == 2:
                    fees += x['close_' + str(j)]
        elif template == 'a3':
            raw = sum(x['claw_' + str(j)] for j, n in enumerate(pair_counts) if n == 1)
            fees = capped(raw, x['group_cap'])
            if count >= 2 and flags[0] == 0:
                fees += x['global_claw']
        elif template == 'a4':
            broken = [j for j, n in enumerate(pair_counts) if n == 1]
            fees = sum(x['claw_' + str(j)] for j in broken)
            if len(broken) >= 2:
                fees -= capped(x['rebate'], fees)
        elif template == 'a5':
            fees = 0
            for j, n in enumerate(pair_counts):
                if n == 1 and x['claw_' + str(j)] > fees:
                    fees = x['claw_' + str(j)]
            if flags[0] and flags[5]:
                fees += x['closure']
        else:
            raise ValueError(template)
        loss = personal + fees
    elif template[0] == 'b':
        gross = sum(x['loss_' + str(i)] for i in affected)
        paid = 0
        if template == 'b1':
            for i in affected:
                above = nonnegative(x['loss_' + str(i)] - x['ded_' + str(i)])
                paid += capped(above, x['cover_' + str(i)])
            paid = capped(paid, x['coverage'])
        elif template == 'b2':
            above = nonnegative(gross - x['deductible'])
            paid = capped(Fraction(above, 2), x['coverage'])
        elif template == 'b3':
            tier = x['small_cap'] if count < 3 else x['large_cap']
            paid = capped(nonnegative(gross - x['deductible']), tier)
        elif template == 'b4':
            first = capped(nonnegative(gross - x['primary_ded']), x['primary_cap'])
            remaining = gross - first
            second = capped(nonnegative(remaining - x['secondary_ded']), x['secondary_cap'])
            paid = first + second
        elif template == 'b5':
            if gross > x['franchise']:
                paid = capped(gross, x['coverage'])
        else:
            raise ValueError(template)
        loss = gross - paid
    elif template[0] == 'c':
        kept = [i for i in range(6) if not flags[i]]
        remaining = sum(x['item_' + str(i)] for i in kept)
        restock = sum(x['restock_' + str(i)] for i in affected)
        freight = sorted(x['freight_' + str(i)] for i in affected)[-1]
        claw = 0
        if template == 'c1':
            for j in range(2):
                group_left = sum(x['item_' + str(i)] for i in range(j * 3, j * 3 + 3) if not flags[i])
                if group_left < x['threshold_' + str(j)]:
                    claw += x['promo_' + str(j)]
        elif template == 'c3':
            if remaining < x['low_threshold']:
                kept_promo = 0
            elif remaining < x['high_threshold']:
                kept_promo = x['low_promo']
            else:
                kept_promo = x['promo']
            claw = x['promo'] - kept_promo
        else:
            if remaining < x['threshold']:
                claw = x['promo']
            if template == 'c2':
                freight = 0
                for left in (0, 2, 4):
                    quotes = [x['freight_' + str(i)] for i in (left, left + 1) if flags[i]]
                    if quotes:
                        freight += sorted(quotes)[-1]
            elif template == 'c4':
                retained_weight = sum(x['weight_' + str(i)] for i in kept)
                if retained_weight < x['weight_threshold']:
                    claw += x['ship_subsidy']
            elif template == 'c5':
                restock = capped(restock, x['restock_cap'])
                returned_value = sum(x['item_' + str(i)] for i in affected)
                if returned_value >= x['free_return_threshold']:
                    freight = 0
            else:
                raise ValueError(template)
        loss = restock + freight + claw
    elif template[0] == 'd':
        replacements = sum(x['replacement_' + str(i)] for i in affected)
        nominal = sum(x['refund_' + str(i)] for i in affected)
        bill = replacements
        if template == 'd1':
            limited = sum(capped(x['refund_' + str(i)], x['item_cap_' + str(i)]) for i in affected)
            paid = capped(limited, x['refund_cap'])
        elif template == 'd2':
            for j, left in enumerate((0, 2, 4)):
                if flags[left] or flags[left + 1]:
                    bill += x['setup_' + str(j)]
            paid = capped(nominal, x['refund_cap'])
        elif template == 'd3':
            paid = capped(nominal, x['small_cap'] if count < 3 else x['large_cap'])
        elif template == 'd4':
            cash = capped(nominal, x['refund_cap'])
            credit = sum(x['credit_' + str(i)] for i in affected)
            usable_credit = Fraction(capped(credit, x['credit_cap']), 2)
            paid = cash + usable_credit
        elif template == 'd5':
            for j, members in enumerate([[0, 1, 2], [2, 3, 4], [0, 4, 5]]):
                if any(flags[i] for i in members):
                    bill += x['dispatch_' + str(j)]
            paid = capped(nominal, x['refund_cap'])
            if replacements >= x['bonus_threshold']:
                paid += x['bonus']
        else:
            raise ValueError(template)
        loss = nonnegative(bill - paid)
    else:
        raise ValueError(template)
    result = Fraction(loss + x['admin'])
    assert result.denominator == 1 and result >= 0
    return result.numerator


def purchase_ok(template, x):
    if x['price'] < 0 or x['price'] > BUDGET:
        return False
    if template[0] != 'c':
        return True
    subtotal = sum(x['item_' + str(i)] for i in range(6))
    if template == 'c1':
        if x['price'] != subtotal - x['promo_0'] - x['promo_1']:
            return False
        return all(sum(x['item_' + str(i)] for i in range(j * 3, j * 3 + 3)) >= x['threshold_' + str(j)] for j in range(2))
    extra = x['ship_subsidy'] if template == 'c4' else 0
    threshold = x['high_threshold'] if template == 'c3' else x['threshold']
    if x['price'] != subtotal - x['promo'] - extra or subtotal < threshold:
        return False
    if template == 'c4':
        return sum(x['weight_' + str(i)] for i in range(6)) >= x['weight_threshold']
    return True


def row_audit(template, attrs, max_affected):
    events = [(mask, cash_loss(template, attrs, mask)) for mask in range(64) if mask.bit_count() <= max_affected]
    worst = sorted(loss for _, loss in events)[-1]
    masks = [mask for mask, loss in events if loss == worst]
    return dict(safe=purchase_ok(template, attrs) and worst <= LIMIT,
                psi=str(BENEFIT - attrs['price'] - worst), worst_loss=worst,
                worst_masks=masks, event_count=len(events))


def reference(template, candidates, max_affected):
    rows = [dict(id=c['id'], **row_audit(template, c['attrs'], max_affected)) for c in candidates]
    eligible = [r for r in rows if r['safe'] and int(r['psi']) > 0]
    if not eligible:
        return dict(decision='reject', allowed_ids=[], guaranteed_utility=None,
                    reason_code='infeasible_complete_catalog', matrix=rows)
    best = sorted(int(r['psi']) for r in eligible)[-1]
    return dict(decision='accept', allowed_ids=[r['id'] for r in eligible if int(r['psi']) == best],
                guaranteed_utility=str(best), reason_code='optimal_certified', matrix=rows)
