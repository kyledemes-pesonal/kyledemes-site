"""Stacked event-study PPML: citations to already-published articles before and after the publisher opened them.

Unit = (stack, journal, publication year[, free-copy flag]); time = citing year; outcome = citations received that year.
Stack = one treated journal's opening + its 5 matched controls (same subfield, closest pre-period citation level and trend
to the treated cohort range, chosen from 12 static nearest neighbours). Window: T-5 .. T+10 (citing years 1995-2025;
2026 is incomplete and never used). The opening year T itself is dropped (donut: dates are month- or year-precise).
FE: unit + stack x citing year + stack x article age. Treated-post coefficient -> % change = exp(b) - 1. SEs clustered by journal.
Usage: .venv/bin/python -I scripts/estimate.py   (writes results/estimates.json, results/event_study.tsv, results/stacks.tsv)
"""
import csv, json, math, collections, sys
import numpy as np, pandas as pd, pyfixest as pf

csv.field_size_limit(10**9)
def rd(p): return list(csv.DictReader(open(p), delimiter='\t', quoting=csv.QUOTE_NONE))
LAST_CY, PRE, POST, NCTRL = 2025, 5, 10, 5

panel = pd.read_csv('data/q08_panel.csv', dtype={'src': 'int64', 'py': 'int64', 'green': 'int64'})
panel['cy'] = panel['cy'].astype('Int64')
sizes = panel.groupby(['src', 'py', 'green'], as_index=False)[['n_articles', 'n_oa_pub_now']].first()
cit = panel.dropna(subset=['cy']).astype({'cy': 'int64'})
events = rd('results/final_events.tsv')
cands = collections.defaultdict(list)
for c in rd('data/control_candidates.tsv'): cands[(c['treated'], c['T'])].append(int(c['control']))

# journal x py x cy cites (summed over free-copy flag) for matching
jc = cit.groupby(['src', 'py', 'cy'])['cites'].sum()
jn = sizes.groupby(['src', 'py'])['n_articles'].sum()
def pre_profile(src, lo, hi, T):
    """cites per article in T-5..T-1 to articles published lo..hi (and <= T-1), and log growth (T-2..T-1 vs T-5..T-4)."""
    try: n = jn.loc[src]
    except KeyError: return None
    n = n[(n.index >= lo) & (n.index <= min(hi, T - 1))].sum()
    if n < 30: return None
    try: c = jc.loc[src]
    except KeyError: return None
    c = c[(c.index.get_level_values('py') >= lo) & (c.index.get_level_values('py') <= min(hi, T - 1))]
    by = c.groupby(level='cy').sum()
    early = by.reindex(range(T - 5, T - 3), fill_value=0).sum(); late = by.reindex(range(T - 2, T), fill_value=0).sum()
    lvl = (early + by.reindex([T - 3], fill_value=0).sum() + late) / n
    return dict(n=n, lvl=lvl, gr=math.log((late + 1) / (early + 1)))

stacks, units = [], []
for k, e in enumerate(events):
    s, T, lo, hi = int(e['source']), int(e['T']), int(e['cohort_from']), int(e['cohort_to'])
    hi = min(hi, T - 1)
    if T + 1 > LAST_CY: continue
    tp = pre_profile(s, lo, hi, T)
    if tp is None or tp['lvl'] == 0: continue
    scored = []
    for c in cands[(e['source'], e['T'])]:
        cp = pre_profile(c, lo, hi, T)
        if cp is None or cp['lvl'] == 0: continue
        d = abs(math.log(cp['lvl']) - math.log(tp['lvl'])) + abs(cp['gr'] - tp['gr']) + 0.25 * abs(math.log(cp['n'] / tp['n']))
        scored.append((d, c))
    scored.sort()
    ctrls = [c for _, c in scored[:NCTRL]]
    if len(ctrls) < 2: continue
    stacks.append(dict(stack=k, treated=s, journal=e['journal'], program=e['program'], T=T, lo=lo, hi=hi,
                       n_date_sources=int(e['n_date_sources']), flip=int(e['flip']), note=e['note'],
                       treated_n=int(tp['n']), treated_pre_lvl=round(tp['lvl'], 3), controls=' '.join(map(str, ctrls)),
                       mean_match_dist=round(sum(d for d, _ in scored[:NCTRL]) / len(ctrls), 3)))
    for j, tr in [(s, 1)] + [(c, 0) for c in ctrls]:
        units.append((k, j, tr, lo, hi, T))
st = pd.DataFrame(stacks)
st.to_csv('results/stacks.tsv', sep='\t', index=False)
print('stacks', len(st), 'treated articles', int(st.treated_n.sum()), file=sys.stderr)

def build(split_green=False, outcome='cites'):
    keys = ['src', 'py', 'green'] if split_green else ['src', 'py']
    cy = cit.groupby(keys + ['cy'], as_index=False)[['cites', 'self_cites']].sum()
    sz = sizes.groupby(keys, as_index=False)[['n_articles', 'n_oa_pub_now']].sum()
    frames = []
    u = pd.DataFrame(units, columns=['stack', 'src', 'treated', 'lo', 'hi', 'T'])
    for (k, T), g in u.groupby(['stack', 'T']):
        lo, hi = g.lo.iloc[0], g.hi.iloc[0]
        a = sz[sz.src.isin(g.src) & sz.py.between(lo, hi) & (sz.n_articles > 0)].merge(g[['src', 'treated']], on='src')
        yrs = pd.DataFrame({'cy': range(max(1995, T - PRE), min(LAST_CY, T + POST) + 1)})
        a = a.merge(yrs, how='cross')
        a = a.merge(cy[cy.src.isin(g.src)], on=keys + ['cy'], how='left').fillna({'cites': 0, 'self_cites': 0})
        a['stack'] = k; a['T'] = T
        frames.append(a)
    d = pd.concat(frames, ignore_index=True)
    d['k'] = d.cy - d['T']; d['age'] = (d.cy - d.py).clip(upper=80)
    d = d[d.k != 0].copy()                                   # donut: drop the opening year
    d['y'] = d['cites'] if outcome == 'cites' else d['cites'] - d['self_cites']
    d['post'] = (d.k >= 1).astype(int); d['tp'] = d.treated * d.post
    d['unit'] = d['stack'].astype(str) + '_' + d.src.astype(str) + '_' + d.py.astype(str) + ('_' + d.green.astype(str) if split_green else '')
    d['s_cy'] = d['stack'].astype(str) + '_' + d.cy.astype(str); d['s_age'] = d['stack'].astype(str) + '_' + d.age.astype(str)
    return d

def pooled(d, label, weights=None):
    try:
        m = pf.fepois('y ~ tp | unit + s_cy + s_age', data=d, vcov={'CRV1': 'src'}, weights=weights)
        b, se = float(m.coef()['tp']), float(m.se()['tp'])
    except Exception as ex:
        print('FAILED', label, ex, file=sys.stderr); return dict(label=label, error=str(ex)[:200])
    r = dict(label=label, b=b, se=se, pct=100 * (math.exp(b) - 1), lo95=100 * (math.exp(b - 1.96 * se) - 1), hi95=100 * (math.exp(b + 1.96 * se) - 1),
             n_obs=int(m._N), n_stacks=int(d['stack'].nunique()), n_treated_journals=int(d[d.treated == 1].src.nunique()))
    print(f"{label:55s} {r['pct']:+6.1f}% [{r['lo95']:+.1f}, {r['hi95']:+.1f}]  stacks {r['n_stacks']}", file=sys.stderr)
    return r

def event_study(d, label):
    d = d.copy()
    for k in range(-PRE, POST + 1):
        if k in (-1, 0): continue
        d[f'e{k + PRE}'] = ((d.k == k) & (d.treated == 1)).astype(int)
    terms = [f'e{k + PRE}' for k in range(-PRE, POST + 1) if k not in (-1, 0)]
    terms = [t for t in terms if d[t].sum() > 0]
    m = pf.fepois('y ~ ' + ' + '.join(terms) + ' | unit + s_cy + s_age', data=d, vcov={'CRV1': 'src'})
    co, se = m.coef(), m.se()
    return [dict(label=label, k=int(t[1:]) - PRE, b=float(co[t]), se=float(se[t]), pct=100 * (math.exp(co[t]) - 1),
                 lo95=100 * (math.exp(co[t] - 1.96 * se[t]) - 1), hi95=100 * (math.exp(co[t] + 1.96 * se[t]) - 1)) for t in terms]

if __name__ == '__main__':
    res, es = [], []
    d = build()
    st_idx = st.set_index('stack')
    d['program'] = d['stack'].map(st_idx.program); d['nds'] = d['stack'].map(st_idx.n_date_sources)
    res.append(pooled(d, 'MAIN: all paywall-removal events'))
    es += event_study(d, 'MAIN')
    # weighting: each stack equal (weights = 1 / stack pre-period citations)
    pre = d[d.k < 0].groupby('stack').y.sum().replace(0, np.nan)
    d['w'] = d['stack'].map(1 / pre).fillna(0) * 1e3
    res.append(pooled(d[d.w > 0], 'each event weighted equally', weights='w'))
    res.append(pooled(d[d.nds >= 2], 'events with >= 2 independent date sources'))
    for p, g in d.groupby('program'):
        if g['stack'].nunique() >= 3: res.append(pooled(g, f'program: {p}'))
    for p in d.program.unique():
        res.append(pooled(d[d.program != p], f'leave out: {p}'))
    # outcomes and screens
    dx = build(outcome='external'); dx['program'] = dx['stack'].map(st_idx.program)
    res.append(pooled(dx, 'excluding same-journal citations'))
    # controls whose cohort content is now >10% publisher-OA dropped (conservative screen)
    oa = sizes.groupby('src')[['n_articles', 'n_oa_pub_now']].sum(); oa_share = (oa.n_oa_pub_now / oa.n_articles)
    bad = set(oa_share[oa_share > 0.10].index)
    res.append(pooled(d[(d.treated == 1) | ~d.src.isin(bad)], 'controls screened: <=10% of articles publisher-OA now'))
    # placebo: fake opening 3 years early, pre-period only
    pl = d[d.k < 0].copy(); pl['tp'] = pl.treated * (pl.cy >= pl['T'] - 3).astype(int)
    res.append(pooled(pl, 'PLACEBO: fake opening 3 years early (pre-period only)'))
    # free-copy split
    dg = build(split_green=True)
    for gval, lab in ((0, 'articles with no repository/PMC copy today'), (1, 'articles with a repository/PMC copy today')):
        res.append(pooled(dg[dg.green == gval], f'split: {lab}'))
    # age at opening
    d['age_T'] = d['T'] - d.py
    for lo, hi, lab in ((1, 5, '1-5 years old at opening'), (6, 15, '6-15 years old'), (16, 40, '16-40 years old'), (41, 400, 'over 40 years old')):
        res.append(pooled(d[d.age_T.between(lo, hi)], f'split: {lab}'))
    json.dump(res, open('results/estimates.json', 'w'), indent=1)
    pd.DataFrame(es).to_csv('results/event_study.tsv', sep='\t', index=False)
