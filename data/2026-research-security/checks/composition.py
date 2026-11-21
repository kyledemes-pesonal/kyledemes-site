"""How much of the drop in the tri-agency/CFI-funded share of Canada-China papers comes from the shift toward
China-led papers (composition), rather than from each type of paper crediting Canadian grants less often?
Input ../results/lead_author.json (scripts/lead_author.py). First-author types: Chinese-only (first_x), Canadian-only
(first_ca), both countries (first_both), other (first_other). Periods 2018-20 vs 2023-25.
Composition effect = funded share with 2018-20 within-type rates and 2023-25 type mix, minus the 2018-20 share,
as a fraction of the actual change. Output ../results/composition.json"""
import json
d = json.load(open('../results/lead_author.json'))
TYPES = ['first_x', 'first_ca', 'first_both', 'first_other']
def tot(key, yrs, t):
    return sum(d[key][str(y)].get(t, 0) for y in yrs)
def period(yrs):
    allp = {t: tot('CN_all', yrs, t) for t in TYPES}
    fund = {t: tot('CN_funded', yrs, t) for t in TYPES}
    n = sum(allp.values())
    return {t: {'papers': allp[t], 'funded': fund[t], 'rate': fund[t] / allp[t] if allp[t] else 0, 'mix': allp[t] / n} for t in TYPES}
pre, post = period(range(2018, 2021)), period(range(2023, 2026))
share = lambda rates, mix: sum(rates[t]['rate'] * mix[t]['mix'] for t in TYPES)
base, actual, counterfactual = share(pre, pre), share(post, post), share(pre, post)
out = {'pre': pre, 'post': post, 'funded_share_pre': base, 'funded_share_post': actual,
       'funded_share_pre_rates_post_mix': counterfactual,
       'composition_fraction_of_change': (counterfactual - base) / (actual - base)}
json.dump(out, open('../results/composition.json', 'w'), indent=1)
print(f"funded share {100*base:.1f}% -> {100*actual:.1f}%; mix alone -> {100*counterfactual:.1f}%; "
      f"composition explains {100*out['composition_fraction_of_change']:.0f}% of the drop")
for t in TYPES:
    print(f"  {t:12} rate {100*pre[t]['rate']:.1f}% -> {100*post[t]['rate']:.1f}%   papers {pre[t]['papers']:,} -> {post[t]['papers']:,}")
