"""Author panel without selection on the outcome (review concern 5).
Cohorts are defined on 2015-2017 activity; outcomes are measured in 2018-2020 (pre) and 2023-2025 (post), so the
selection window does not overlap the base.
- A': Canadian authors with a Canadian authorship on a (verified) NRO work in 2015-17.
- B': Canadian authors with a Canadian authorship on a control-institution work in 2015-17 and no NRO work 2015-17.
Outcome: pooled share of the cohort's Canadian papers (funded / other) with an NRO (A') or a control institution (B').
Effect = change in log share for A' minus change for B', funded and other separately; 95% CI by author bootstrap
(1,000 draws). Run with VERIFIED=1. Output ../results/panel_rebase.json"""
import os
import json, random, math, collections, sys
sys.argv = sys.argv[:1]
import author_panel as ap
A, B0, nro_early = set(), set(), set()
rows = collections.defaultdict(lambda: [0] * 8)   # (author, period) -> n, nf, nro, nro_f, ctl, ctl_f
seen = set(); W = []
for w in ap.works():
    if w['w'] in seen or not w['y']: continue
    seen.add(w['w'])
    nro, ctl, cn, fu = ap.flags(w)
    ca = {a[0] for a in w['a'] if 'CA' in a[3] and a[0]}
    if 2015 <= w['y'] <= 2017:
        if nro: A |= ca; nro_early |= ca
        if ctl: B0 |= ca
    per = 'pre' if 2018 <= w['y'] <= 2020 else 'post' if 2023 <= w['y'] <= 2025 else None
    if per and ca: W.append((per, ca, nro, ctl, fu))
B = B0 - nro_early
for per, ca, nro, ctl, fu in W:
    for a in ca & (A | B):
        r = rows[(a, per)]
        v = [1, fu, nro, nro and fu, ctl, ctl and fu]
        for i, x in enumerate(v): r[i] += int(bool(x))
def share(auth, per, k, funded):
    num = den = 0
    for a in auth:
        r = rows.get((a, per))
        if not r: continue
        if funded: num += r[k + 1]; den += r[1]
        else: num += r[k] - r[k + 1]; den += r[0] - r[1]
    return num / den if den and num else None
def effect(Aa, Bb, funded):
    a0, a1 = share(Aa, 'pre', 2, funded), share(Aa, 'post', 2, funded)
    b0, b1 = share(Bb, 'pre', 4, funded), share(Bb, 'post', 4, funded)
    return a0, a1, b0, b1, math.log(a1 / a0) - math.log(b1 / b0)
A, B = sorted(A), sorted(B)
out = {'definitions': __doc__, 'n_A': len(A), 'n_B': len(B)}
random.seed(11)
for funded in (True, False):
    a0, a1, b0, b1, e = effect(A, B, funded)
    boots = []
    for _ in range(1000):
        boots.append(effect([random.choice(A) for _ in A], [random.choice(B) for _ in B], funded)[4])
    boots.sort(); lo, hi = boots[25], boots[974]
    k = 'funded' if funded else 'other'
    out[k] = {'A_pre': a0, 'A_post': a1, 'B_pre': b0, 'B_post': b1, 'A_change': a1 / a0 - 1, 'B_change': b1 / b0 - 1,
              'effect_pct': math.exp(e) - 1, 'ci95': [math.exp(lo) - 1, math.exp(hi) - 1]}
    print(k, f"A' {100*a0:.1f}->{100*a1:.1f}% ({100*(a1/a0-1):+.0f}%)  B' {100*b0:.1f}->{100*b1:.1f}% ({100*(b1/b0-1):+.0f}%)  A' vs B': {100*(math.exp(e)-1):+.0f}% [{100*(math.exp(lo)-1):+.0f}, {100*(math.exp(hi)-1):+.0f}]")
print("n A'", len(A), "B'", len(B))
assert os.environ.get('VERIFIED') == '1', 'run with VERIFIED=1: the output file is the verified result'
json.dump(out, open('../results/panel_rebase.json', 'w'), indent=1)
