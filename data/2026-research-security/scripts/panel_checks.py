"""Robustness checks on the re-based researcher panel (panel_rebase.py), as quoted in the post's caveats:
(a) ORCID-only authors; (b) 95% interval from a bootstrap that resamples home institutions (researchers at the same
university move together); (c) placebo windows that end before 2021, and the yearly pooled shares.
Run with VERIFIED=1 after author_panel.py and provinces_v2.py (which caches institution records with their region in
../results/funded_fulltext_cache/ca_institutions.json). Output ../results/panel_checks.json (no author IDs)."""
import os, sys, json, math, random, collections
os.environ['VERIFIED'] = '1'; sys.argv = sys.argv[:1]
import author_panel as ap
INST = json.load(open('../results/funded_fulltext_cache/ca_institutions.json'))
reg = {i: r.get('r') for i, r in INST.items() if r.get('cc') == 'CA'}
W, seen, orc, home = [], set(), {}, collections.defaultdict(collections.Counter)
for w in ap.works():
    if w['w'] in seen or not w['y']: continue
    seen.add(w['w'])
    nro, ctl, cn, fu = ap.flags(w)
    ca = [a for a in w['a'] if 'CA' in a[3] and a[0]]
    if 2015 <= w['y'] <= 2017:
        for a in ca:
            orc[a[0]] = orc.get(a[0], False) or a[1]
            cand = [x for x in a[2] if reg.get(x)]   # home institution: a lineage ID with a Canadian region
            if cand: home[a[0]][cand[-1]] += 1
    ids = frozenset(a[0] for a in ca)
    if ids: W.append((w['y'], ids, nro, ctl, fu))
pct = lambda x: 100 * (math.exp(x) - 1)

def build(coh, pre, post):
    A, B0 = set(), set()
    for y, ids, nro, ctl, fu in W:
        if y in coh:
            if nro: A |= ids
            if ctl: B0 |= ids
    B = B0 - A
    rows = collections.defaultdict(lambda: [0] * 6); yr = collections.defaultdict(lambda: [0] * 6)
    for y, ids, nro, ctl, fu in W:
        per = 'pre' if y in pre else 'post' if y in post else None
        v = [1, fu, nro, nro and fu, ctl, ctl and fu]
        for a in ids:
            if a in A or a in B:
                if per:
                    r = rows[(a, per)]
                    for i, x in enumerate(v): r[i] += int(bool(x))
                r2 = yr[('A' if a in A else 'B', y)]
                for i, x in enumerate(v): r2[i] += int(bool(x))
    def share(auth, per, k, funded):
        num = den = 0
        for a in auth:
            r = rows.get((a, per))
            if not r: continue
            if funded: num += r[k + 1]; den += r[1]
            else: num += r[k] - r[k + 1]; den += r[0] - r[1]
        return num / den
    def eff(Aa, Bb, funded):
        return math.log(share(Aa, 'post', 2, funded) / share(Aa, 'pre', 2, funded)) - math.log(share(Bb, 'post', 4, funded) / share(Bb, 'pre', 4, funded))
    return sorted(A), sorted(B), eff, yr

out = {}
A, B, eff, yr = build({2015, 2016, 2017}, {2018, 2019, 2020}, {2023, 2024, 2025})
# (a) ORCID-only
Ao = [a for a in A if orc.get(a)]; Bo = [a for a in B if orc.get(a)]
out['orcid_only'] = {'n_A': len(Ao), 'n_B': len(Bo), **{k: round(pct(eff(Ao, Bo, f)), 1) for k, f in (('funded', True), ('other', False))}}
# (b) institution-cluster bootstrap
hm = {a: (home[a].most_common(1)[0][0] if home[a] else 'none') for a in A + B}
cl = collections.defaultdict(lambda: ([], []))
for a in A: cl[hm[a]][0].append(a)
for a in B: cl[hm[a]][1].append(a)
keys = sorted(cl); random.seed(5); out['cluster_bootstrap'] = {'clusters': len(keys), 'draws': 300}
for k, funded in (('funded', True), ('other', False)):
    bs = []
    for _ in range(300):
        Aa, Bb = [], []
        for c in (random.choice(keys) for _ in keys): Aa += cl[c][0]; Bb += cl[c][1]
        try: bs.append(eff(Aa, Bb, funded))
        except ZeroDivisionError: pass
    bs.sort()
    out['cluster_bootstrap'][k] = {'effect': round(pct(eff(A, B, funded)), 1),
                                   'ci95': [round(pct(bs[int(.025 * len(bs))]), 1), round(pct(bs[int(.975 * len(bs)) - 1]), 1)]}
# yearly pooled funded shares (A: listed share of funded papers; B: control share)
out['yearly'] = {y: {'A_funded': round(yr[('A', y)][3] / yr[('A', y)][1], 4), 'B_funded': round(yr[('B', y)][5] / yr[('B', y)][1], 4)}
                 for y in range(2015, 2026)}
# (c) placebo and other windows (point estimates)
WIN = {'placebo coh15 pre16-17 post19-20': ({2015}, {2016, 2017}, {2019, 2020}),
       'placebo coh15 pre16 post18': ({2015}, {2016}, {2018}),
       'placebo coh15-16 pre17-18 post20-21': ({2015, 2016}, {2017, 2018}, {2020, 2021}),
       'midpoint coh15-17 pre18-20 post21-22': ({2015, 2016, 2017}, {2018, 2019, 2020}, {2021, 2022}),
       'later coh18-20 pre21-22 post24-25': ({2018, 2019, 2020}, {2021, 2022}, {2024, 2025})}
out['windows'] = {}
for name, (c, p0, p1) in WIN.items():
    a_, b_, e_, _ = build(c, p0, p1)
    out['windows'][name] = {'n_A': len(a_), 'n_B': len(b_), 'funded': round(pct(e_(a_, b_, True)), 1), 'other': round(pct(e_(a_, b_, False)), 1)}
json.dump(out, open('../results/panel_checks.json', 'w'), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != 'yearly'}, indent=1))
