"""Within-journal test: opened volumes vs the same journal's volumes that stayed closed over the window.
Stack x citing-year FE absorb anything that hits the whole journal at T (a front-list flip, new platform, publicity).
 Annual Reviews 2023 joiners: treated = previous nine volumes (opened), control = volumes 2000-2013 (still closed).
 Royal Society 2011: treated = papers older than 70 years (<= 1941), control = 1960-1985 papers (not reached by the rolling
 70-year wall before 2026). Window T-5..T+10 (to 2025), donut at T, FE unit + stack x citing year + stack x age, journal clusters."""
import csv, math, sys
import pandas as pd, pyfixest as pf
sys.argv = sys.argv[:1]
import importlib.util
spec = importlib.util.spec_from_file_location('est', 'scripts/estimate.py'); est = importlib.util.module_from_spec(spec); spec.loader.exec_module(est)
cit, sizes = est.cit, est.sizes
def rd(p): return list(csv.DictReader(open(p), delimiter='\t', quoting=csv.QUOTE_NONE))
ev = rd('results/final_events.tsv')
def run(prog, ctrl_lo, ctrl_hi, label):
    frames = []
    for k, e in enumerate(ev):
        if e['program'] != prog: continue
        s, T, lo, hi = int(e['source']), int(e['T']), int(e['cohort_from']), min(int(e['cohort_to']), int(e['T']) - 1)
        cy = cit[cit.src == s].groupby(['py', 'cy'], as_index=False)[['cites']].sum()
        sz = sizes[sizes.src == s].groupby('py', as_index=False).n_articles.sum()
        sz = sz[(sz.n_articles > 0) & (sz.py.between(lo, hi) | sz.py.between(ctrl_lo, ctrl_hi))].copy()
        sz['treated'] = sz.py.between(lo, hi).astype(int)
        if sz.treated.sum() == 0 or (1 - sz.treated).sum() == 0: continue
        a = sz.merge(pd.DataFrame({'cy': range(max(1995, T - 5), min(2025, T + 10) + 1)}), how='cross').merge(cy, on=['py', 'cy'], how='left').fillna({'cites': 0})
        a['stack'] = k; a['T'] = T; a['src'] = s; frames.append(a)
    d = pd.concat(frames, ignore_index=True)
    d['k'] = d.cy - d['T']; d = d[d.k != 0].copy(); d['age'] = (d.cy - d.py).clip(upper=80)
    d['tp'] = d.treated * (d.k >= 1).astype(int); d['y'] = d.cites
    d['unit'] = d['stack'].astype(str) + '_' + d.py.astype(str)
    d['s_cy'] = d['stack'].astype(str) + '_' + d.cy.astype(str); d['s_age'] = d['stack'].astype(str) + '_' + d.age.astype(str)
    m = pf.fepois('y ~ tp | unit + s_cy + s_age', data=d, vcov={'CRV1': 'src'})
    b, se = float(m.coef()['tp']), float(m.se()['tp'])
    r = dict(label=label, pct=100 * (math.exp(b) - 1), lo95=100 * (math.exp(b - 1.96 * se) - 1), hi95=100 * (math.exp(b + 1.96 * se) - 1), journals=int(d.src.nunique()))
    # placebo: 3 years early, pre-period only
    p = d[d.k < 0].copy(); p['tp'] = p.treated * (p.cy >= p['T'] - 3).astype(int)
    try:
        mp = pf.fepois('y ~ tp | unit + s_cy + s_age', data=p, vcov={'CRV1': 'src'}); bp, sp = float(mp.coef()['tp']), float(mp.se()['tp'])
        r.update(placebo_pct=100 * (math.exp(bp) - 1), placebo_lo95=100 * (math.exp(bp - 1.96 * sp) - 1), placebo_hi95=100 * (math.exp(bp + 1.96 * sp) - 1))
    except Exception as ex: r['placebo_error'] = str(ex)[:100]
    print(r); return r
import json
out = [run('Annual Reviews S2O 2023 (previous nine volumes)', 2000, 2013, 'WITHIN: Annual Reviews 2023, opened nine volumes vs older closed volumes'),
       run('Royal Society archive 2011', 1960, 1985, 'WITHIN: Royal Society 2011, pre-1942 papers vs 1960-1985 papers')]
json.dump(out, open('results/estimates_within.json', 'w'), indent=1)
