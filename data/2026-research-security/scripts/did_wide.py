"""Event study with a 24-country donor pool (review concern 2). Same estimator as did.py (spec 'all', base 2018-20):
b[f,p,t] = (r[f,p,t]-r[f,p,B]) - mean over the other 23 focal countries. Permutation inference: each focal country's
coefficient computed as if treated; Canada's rank among 24. Output ../results/event_study_wide.json"""
import json, math
d = json.load(open('../results/pairs_wide.json'))
FOCAL = sorted(d)
COMP = ['US', 'GB', 'DE', 'FR', 'AU', 'JP', 'IT', 'NL', 'CH', 'SE', 'ES', 'KR', 'IN', 'BR', 'TR']
YEARS = range(2010, 2026); BASE = (2018, 2019, 2020)
def r(f, p, t):
    row = d[f][str(t)]; N = row[f]
    comps = [q for q in COMP if q not in (f, p)]
    return math.log(row[p] / N) - sum(math.log(row[q] / N) for q in comps) / len(comps)
def dev(f, p, t): return r(f, p, t) - sum(r(f, p, b) for b in BASE) / 3
out = {}
for p in ['CN', 'HK', 'IR', 'RU']:
    out[p] = {}
    for f in FOCAL:
        if f == p: continue
        peers = [g for g in FOCAL if g not in (f, p)]
        out[p][f] = {t: dev(f, p, t) - sum(dev(g, p, t) for g in peers) / len(peers) for t in YEARS}
json.dump(out, open('../results/event_study_wide.json', 'w'))
pct = lambda x: 100 * (math.exp(x) - 1)
for p in ['CN', 'HK', 'IR', 'RU']:
    v = {f: (out[p][f][2024] + out[p][f][2025]) / 2 for f in out[p]}
    order = sorted(v, key=v.get)
    print(f"== {p}: Canada series", ' '.join(f"{t}:{pct(out[p]['CA'][t]):+.0f}" for t in (2015, 2017, 2019, 2021, 2022, 2023, 2024, 2025)))
    print(f"   2024-25 avg rank of CA: {order.index('CA')+1} of {len(order)} (one-sided permutation p = {(order.index('CA')+1)/len(order):.2f})")
    print('   ', ' '.join(f"{f}:{pct(v[f]):+.0f}" for f in order))
# Leave-one-out: drop each other focal country from the comparison pool in turn; Canada's China gap, 2024-25 average
loo = {}
for g in FOCAL:
    if g in ('CA', 'CN'): continue
    peers = [x for x in FOCAL if x not in ('CA', 'CN', g)]
    v = [dev('CA', 'CN', t) - sum(dev(x, 'CN', t) for x in peers) / len(peers) for t in (2024, 2025)]
    loo[g] = pct(sum(v) / 2)
print(f"   CN leave-one-out, Canada 2024-25: {min(loo.values()):+.1f}% to {max(loo.values()):+.1f}%")
