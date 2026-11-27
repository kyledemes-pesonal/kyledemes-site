"""v4 (27 Nov 2026), steps 2-3: citation change for papers 1-2 years old at opening, against matched controls of the same
publication year, with the v3 model and inference. Read-only on v1-v3 (imports v3_common / v2_common, never calls their
dump functions); writes only results/v4_recent/estimates.json (+ stderr log captured by the caller).

Model (unchanged from v3): stacked PPML, FE unit (stack x journal x publication year) + stack x citing year + stack x age,
donut at T (k = 0 dropped), window T-5..T+10 capped at citing year 2025, the same v3 matched controls (match3: 5 per opening,
same subfield, closest pre-period level and trend of the whole opened cohort). The age band is a subset of the v3 stacked
panel: rows whose publication year is T-1 or T-2, treated and control alike (same rule as v3's age split, v3_extras.py).
Inference: CRV1 by program-date (pd) with t(G-1), score wild-cluster bootstrap (six-point weights, 9,999 draws, null imposed) p and
test-inversion 95% CI, MDE at 80% power ((t_.975 + t_.80) x SE); journal-clustered CI and MDE alongside. Bootstrap only when
G >= 6 program-date clusters.
Weights: citation-weighted = unweighted PPML. Event- and article-weighted re-normalised inside the age band (each opening
counts equally / by its papers in the band); v3's stack-level weights (as in v3's age split) are reported alongside.

Sets:
 A. pure, v3 cohorts (only age-2 papers exist: no pure cohort reaches T-1).
 B. pure, short run (k = 1..2) and a placebo with the same ages: cohort T-5 at a fake opening T-3 (ages 0-1 before,
    3-4 after, all before the real opening).
 C. v4 extension: add the T-1 cohort of pure openings in 12-month-wall programs (Cell Press 2005; Elsevier joiners whose
    list says "embargo 12 months"); those papers opened month by month during year T, the dropped year. Age 1 alone and 1-2.
 D. event study, pure age 2 (lead k = -2 vs ref -1; lags +1..+10), journal clusters.
 E. flips and S2O (front list opened at the same time): Annual Reviews 2023, pilots, other flips with / without platform
    moves, all.
 F. within journal, Annual Reviews S2O 2023 (all journals opened on one date):
    W1 same journal only: recent opened volumes (T-2..T-1) and older opened volumes (2014..T-3), each against the same
       journal's volumes that stayed closed (2000-2013), FE unit + journal x citing year + journal x age (v1 estimate_within
       design on the v3 panel), journal clusters;
    W2 triple difference with the matched controls: (recent opened volumes vs matched controls' same years) minus (the same
       journal's closed 2000-2013 volumes vs the same controls' 2000-2013 volumes).
Run: .venv/bin/python -I scripts/v4_estimates.py 2> results/v4_recent/estimates.log"""
import sys, os, json, math, warnings, time
warnings.filterwarnings('ignore')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # published copy: the folder above scripts/
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from v3_common import *  # noqa
import v3_common as V, v2_common as C
OUT4 = os.path.join(ROOT, 'results', 'v4_recent')
C.OUT = OUT4; V.OUT3 = OUT4  # safety: nothing can be written to v2/v3
B = 9999
res = []
def save(): json.dump(res, open(os.path.join(OUT4, 'estimates.json'), 'w'), indent=1, default=float)
def log(*a): print(*a, file=sys.stderr, flush=True)

ct, sz = V.use_panel(clean=True)
st, units = match3()
d = add_weights(build(st, units))           # v3 stack-level weights kept as we3/wa3
d = d.rename(columns={'we': 'we3', 'wa': 'wa3'})
d['ageT'] = d['T'] - d.py
d['ar'] = np.where(d.program.str.startswith('Annual Reviews S2O 2023'), 'ar2023',
                   np.where(d.program.str.startswith('Annual Reviews S2O pilot'), 'arpilot', ''))

def renorm(x):
    """event-/article-weights inside the subset: we = 1 / subset pre-period citations of the stack; wa = we x subset papers."""
    x = x.copy()
    pre = x[x.k < 0].groupby('stack').y.sum().replace(0, np.nan)
    x['we'] = x['stack'].map(1 / pre).fillna(0) * 1e3
    nb = x[x.treated == 1].drop_duplicates(['stack', 'src', 'py']).groupby('stack').n_articles.sum()
    x['wa'] = x['we'] * x['stack'].map(nb).fillna(0) / 1e3
    return x

def meta(x):
    t = x[x.treated == 1].drop_duplicates(['stack', 'src', 'py'])
    return dict(openings=int(t['stack'].nunique()), papers=int(t.n_articles.sum()), G_pd=int(x[x.treated == 1].pd.nunique()),
                post_years_max=int(x[(x.treated == 1)].k.max()))

def mde_src(se): return pct((1.96 + 0.8416) * se)

def drop_sep(x):
    """Drop rows in FE groups whose outcome is all zero (PPML drops them anyway), so the program-date cluster count the
    bootstrap draws for equals the clusters left in the fitted data (v2 PPMLData counts clusters before PPML's drops)."""
    while True:
        n0 = len(x)
        for fe in ('unit', 's_cy', 's_age'):
            x = x[x.groupby(fe).y.transform('sum') > 0]
        if len(x) == n0: return x

def run(x, label, item, weights=('citation-weighted', 'event-weighted', 'article-weighted'), boot=True, v3w=True):
    x = renorm(x); m = meta(x); x = drop_sep(x)
    W = {'citation-weighted': None, 'event-weighted': 'we', 'article-weighted': 'wa',
         'event-weighted (v3 stack weights)': 'we3', 'article-weighted (v3 stack weights)': 'wa3'}
    wl_all = list(weights) + (['event-weighted (v3 stack weights)', 'article-weighted (v3 stack weights)'] if v3w else [])
    for wl in wl_all:
        w = W[wl]; xx = x if w is None else x[x[w] > 0]
        r = pooled(xx, f'{label} | {wl} (journal clusters)', weights=w, cluster='src')
        if 'error' in r: res.append(dict(item=item, set=label, weight=wl, **m, **r)); continue
        out = dict(item=item, set=label, weight=wl, **m, pct=r['pct'], b=r['b'], src_se=r['se'], src_lo95=r['lo95'], src_hi95=r['hi95'],
                   G_src=r['G'], mde80_src=mde_src(r['se']), n_obs=r['n_obs'])
        G = int(xx.pd.nunique())
        if boot and G >= 6 and not wl.endswith('(v3 stack weights)'):
            t0 = time.time()
            try: ci = clustered_inference(xx, f'{label} | {wl}', weights=w, cluster='pd', B=B)
            except Exception as ex: log('   bootstrap FAILED', ex); ci = dict(boot_error=str(ex)[:200]); out['boot_error'] = ci['boot_error']
            out.update({k: ci[k] for k in ('se', 'G', 't_lo95', 't_hi95', 'boot_p_zero', 'boot_lo95', 'boot_hi95', 'mde80_crv_t', 'mde80_boot') if k in ci})
            out['pd_se'] = out.pop('se', None); out['G_pd_used'] = out.pop('G', None)
            log(f'   bootstrap {time.time() - t0:.0f}s')
        elif G >= 2 and not wl.endswith('(v3 stack weights)'):
            r2 = pooled(xx, f'{label} | {wl} (pd clusters, no bootstrap: G={G})', weights=w, cluster='pd')
            if 'error' not in r2:
                from scipy import stats
                tc = stats.t.ppf(0.975, G - 1); t8 = stats.t.ppf(0.80, G - 1)
                out.update(pd_se=r2['se'], G_pd_used=G, t_lo95=pct(r2['b'] - tc * r2['se']), t_hi95=pct(r2['b'] + tc * r2['se']),
                           mde80_crv_t=pct((tc + t8) * r2['se']), note_pd=f'only {G} program-date clusters: no bootstrap')
        res.append(out); save()

# ---------------- A. pure, v3 cohorts, papers 1-2 years old at opening (= age 2 only) ----------------
P = d[d.group == 'pure']
A = P[P.ageT.isin([1, 2])]
log('A', meta(A))
run(A, 'pure, papers 1-2 years old at opening (v3 cohorts: age 2 only)', 'A')
run(A[A.program != 'Cell Press archive 2005'], 'pure, age 2, without Cell Press', 'A', weights=('citation-weighted', 'event-weighted', 'article-weighted'))
run(A[A.program == 'Cell Press archive 2005'], 'pure, age 2, Cell Press 2005 only', 'A', boot=False, v3w=False)
run(A[A.program == 'Elsevier open archive join'], 'pure, age 2, Elsevier joiners only', 'A', v3w=False)
# reference: v3's own age split recomputed here, papers 1-5 years old (v3: +1.4%, -3.3 to +6.4, journal clusters)
run(P[P.ageT.between(1, 5)], 'pure, papers 1-5 years old (v3 split, recomputed)', 'A-ref', weights=('citation-weighted',), boot=False, v3w=False)
run(P[P.ageT.between(3, 5) & P['stack'].isin(A['stack'].unique())], 'pure, papers 3-5 years old, same 39 openings', 'A-ref', weights=('citation-weighted', 'event-weighted'), boot=False, v3w=False)

# ---------------- B. short run and placebo with the same ages ----------------
dsr = build(st, units, pre=5, post=2); dsr['ageT'] = dsr['T'] - dsr.py
Bsr = dsr[(dsr.group == 'pure') & (dsr.ageT == 2)]
run(Bsr, 'pure, age 2, short run (k = 1..2 only)', 'B', weights=('citation-weighted', 'event-weighted'), v3w=False)
a2_stacks = set(A['stack'].unique())
upl = [(k, j, tr, max(lo, T - 5), T - 5, T - 3) for (k, j, tr, lo, hi, T) in units if k in a2_stacks and lo <= T - 5]
dpl = build(st, upl, pre=5, post=2)   # fake opening T' = T-3; post = T-2..T-1, before the real opening
run(dpl[dpl.group == 'pure'], 'PLACEBO pure, cohort aged 2 at a fake opening 3 years early (post k = 1..2)', 'B', weights=('citation-weighted', 'event-weighted'), v3w=False)

# ---------------- C. v4 extension: T-1 cohorts of 12-month-wall pure openings ----------------
def wall12(r): return (r.program == 'Cell Press archive 2005') or (r.program == 'Elsevier open archive join' and 'embargo 12 months' in str(r.note))
ext = {int(r['stack']) for _, r in st.iterrows() if r.group == 'pure' and wall12(r) and int(r.hi) == int(r['T']) - 2}
uext = [(k, j, tr, lo, (T - 1 if k in ext else hi), T) for (k, j, tr, lo, hi, T) in units if k in ext]
dext = build(st, uext); dext['ageT'] = dext['T'] - dext.py
run(dext[dext.ageT == 1], 'EXT pure 12-month-wall programs, age 1 (T-1 cohort, opened during the dropped year T)', 'C', v3w=False)
run(dext[dext.ageT.isin([1, 2])], 'EXT pure 12-month-wall programs, ages 1-2', 'C', v3w=False)
run(dext[dext.ageT.isin([1, 2]) & (dext.program != 'Cell Press archive 2005')], 'EXT ages 1-2, without Cell Press', 'C', weights=('citation-weighted', 'event-weighted', 'article-weighted'), v3w=False)

# ---------------- D. event study, pure age 2 ----------------
try:
    ks, b, Vc = event_study(A, pre=2, post=10)
    es = [dict(k=k, pct=pct(b[i]), lo95=pct(b[i] - 1.96 * math.sqrt(Vc[i, i])), hi95=pct(b[i] + 1.96 * math.sqrt(Vc[i, i]))) for i, k in enumerate(ks)]
    pd.DataFrame(es).to_csv(os.path.join(OUT4, 'event_study_age2_pure.tsv'), sep='\t', index=False)
    res.append(dict(item='D', set='event study, pure age 2, ref k = -1, journal clusters', rows=es)); save()
    log('event study', [(e['k'], round(e['pct'], 1)) for e in es])
except Exception as ex:
    res.append(dict(item='D', error=str(ex)[:300])); log('ES failed', ex)

# ---------------- E. flips and S2O, papers 1-2 years old at opening ----------------
F = d[(d.group != 'pure') & d.ageT.isin([1, 2])]
run(F[F.ar == 'ar2023'], 'FLIPS Annual Reviews S2O 2023 (42 journals, one date), ages 1-2', 'E', boot=False)
run(F[F.ar == 'arpilot'], 'FLIPS Annual Reviews S2O pilots, ages 1-2', 'E', boot=False, v3w=False)
run(F[F.ar != ''], 'FLIPS Annual Reviews S2O all, ages 1-2', 'E', boot=False)
run(F[(F.ar == '') & (F.platform_move == 0)], 'FLIPS other flips / front list, no platform move, ages 1-2', 'E', v3w=False)
run(F[(F.ar == '')], 'FLIPS other flips incl. platform moves, ages 1-2', 'E', v3w=False)
run(F[F.platform_move == 0], 'FLIPS all (Annual Reviews + other), no platform move, ages 1-2', 'E')
run(F, 'FLIPS all incl. platform moves, ages 1-2', 'E', v3w=False)

# ---------------- F. within journal, Annual Reviews S2O 2023 ----------------
AR = st[st.program.str.startswith('Annual Reviews S2O 2023')]
CL_LO, CL_HI = 2000, 2013
def within_ar(recent_split=True):
    frames = []
    for _, r in AR.iterrows():
        s, T, lo, hi = int(r.treated), int(r['T']), int(r.lo), int(r.hi)
        z = sz[(sz.src == s) & (sz.n_articles > 0) & (sz.py.between(lo, hi) | sz.py.between(CL_LO, CL_HI))].copy()
        z['opened'] = z.py.between(lo, hi).astype(int)
        if z.opened.sum() == 0 or (1 - z.opened).sum() == 0: continue
        a = z.merge(pd.DataFrame({'cy': range(max(1995, T - 5), min(2025, T + 10) + 1)}), how='cross')
        a = a.merge(ct[ct.src == s][['py', 'cy', 'cites']], on=['py', 'cy'], how='left').fillna({'cites': 0})
        a['stack'] = int(r['stack']); a['T'] = T; frames.append(a)
    x = pd.concat(frames, ignore_index=True)
    x['k'] = x.cy - x['T']; x = x[x.k != 0].copy(); x['age'] = (x.cy - x.py).clip(upper=80); x['y'] = x.cites
    x['post'] = (x.k >= 1).astype(int); x['recent'] = ((x.opened == 1) & (x['T'] - x.py <= 2)).astype(int)
    x['tp'] = x.opened * x.post; x['tp_recent'] = x.recent * x.post; x['tp_older'] = (x.opened - x.recent) * x.post
    x['unit'] = x['stack'].astype(str) + '_' + x.py.astype(str)
    x['s_cy'] = x['stack'].astype(str) + '_' + x.cy.astype(str); x['s_age'] = x['stack'].astype(str) + '_' + x.age.astype(str)
    return x
wx = within_ar()
import pyfixest as pf
def fit(x, fml, label, terms):
    m = pf.fepois(fml, data=x, vcov={'CRV1': 'src'})
    co, se = m.coef(), m.se()
    out = dict(item='F', set=label, journals=int(x.src.nunique()), n_obs=int(m._N))
    for t in terms:
        out[t] = dict(pct=pct(co[t]), lo95=pct(co[t] - 1.96 * se[t]), hi95=pct(co[t] + 1.96 * se[t]), se=float(se[t]), mde80_src=mde_src(float(se[t])))
    log(label, {t: round(out[t]['pct'], 1) for t in terms}, {t: (round(out[t]['lo95'], 1), round(out[t]['hi95'], 1)) for t in terms})
    return out, m
o, _ = fit(wx, 'y ~ tp | unit + s_cy + s_age', 'W1 check: AR 2023 all opened volumes vs closed 2000-2013 (v1 design, v3 panel; v1 gave -1.3%)', ['tp'])
res.append(o)
o, _ = fit(wx, 'y ~ tp_recent + tp_older | unit + s_cy + s_age', 'W1: AR 2023, opened volumes aged 1-2 and aged 3-9 at opening, each vs closed 2000-2013 volumes of the same journal', ['tp_recent', 'tp_older'])
t = wx[wx.recent == 1].drop_duplicates(['stack', 'py'])
o.update(papers_recent=int(t.n_articles.sum()), papers_closed=int(wx[wx.opened == 0].drop_duplicates(['stack', 'py']).n_articles.sum()))
res.append(o); save()
# W2: triple difference with the matched controls
st_b = AR.copy(); st_b['stack'] = st_b['stack'] + 100000; st_b['lo'] = CL_LO; st_b['hi'] = CL_HI
has_closed = {int(r['stack']) for _, r in AR.iterrows() if sz[(sz.src == r.treated) & sz.py.between(CL_LO, CL_HI) & (sz.n_articles > 0)].shape[0] > 0}
ub = [(k + 100000, j, tr, CL_LO, CL_HI, T) for (k, j, tr, lo, hi, T) in units if k in has_closed]
db = build(pd.concat([st, st_b], ignore_index=True), ub); db['ageT'] = db['T'] - db.py
da = d[d['stack'].isin(has_closed)]
for lab, aa in (('recent (aged 1-2)', da[da.ageT.isin([1, 2])]), ('all opened (2014-2022)', da)):
    x = pd.concat([aa.assign(cohort='A'), db.assign(cohort='B')], ignore_index=True)
    x['tpA'] = x.tp * (x.cohort == 'A'); x['tpB'] = x.tp * (x.cohort == 'B')
    m = pf.fepois('y ~ tpA + tpB | unit + s_cy + s_age', data=x, vcov={'CRV1': 'src'})
    co = m.coef(); Vm = pd.DataFrame(m._vcov, index=co.index, columns=co.index)
    dd_ = co['tpA'] - co['tpB']; sdd = math.sqrt(Vm.loc['tpA', 'tpA'] + Vm.loc['tpB', 'tpB'] - 2 * Vm.loc['tpA', 'tpB'])
    se = m.se()
    o = dict(item='F', set=f'W2: AR 2023 triple difference, {lab} opened volumes minus closed 2000-2013 volumes, each vs matched controls',
             journals=len(has_closed), G_src=int(x.src.nunique()),
             opened_vs_controls=dict(pct=pct(co['tpA']), lo95=pct(co['tpA'] - 1.96 * se['tpA']), hi95=pct(co['tpA'] + 1.96 * se['tpA'])),
             closed_vs_controls=dict(pct=pct(co['tpB']), lo95=pct(co['tpB'] - 1.96 * se['tpB']), hi95=pct(co['tpB'] + 1.96 * se['tpB'])),
             triple_difference=dict(pct=pct(dd_), lo95=pct(dd_ - 1.96 * sdd), hi95=pct(dd_ + 1.96 * sdd), se=sdd, mde80_src=mde_src(sdd)))
    log(o['set'], {k: (round(v['pct'], 1), round(v['lo95'], 1), round(v['hi95'], 1)) for k, v in o.items() if isinstance(v, dict)})
    res.append(o); save()
log('done')

# ---------------- G. diagnostics added after the first run (27 Nov): placebos with the same ages ----------------
# Annual Reviews 2023: cohorts aged 1-2 at a fake opening in 2020 (py 2018-2019), post = 2021-2022, before the real 2023
# opening; same matched controls. Compare with the real AR 2023 ages 1-2 estimate (post = 2024-2025, also two years).
try:
    ar_st = set(AR['stack'])
    upa = [(k, j, tr, max(lo, T - 5), T - 4, T - 3) for (k, j, tr, lo, hi, T) in units if k in ar_st and lo <= T - 5]
    dpa = build(st, upa, pre=5, post=2)
    run(dpa, 'PLACEBO AR 2023, cohorts aged 1-2 at a fake opening in 2020 (post 2021-2022)', 'G', boot=False, v3w=False)
except Exception as ex: log('G1 failed', ex); res.append(dict(item='G', error=str(ex)[:300]))
# pure age-2 placebo and event study by program
try:
    for prog in ('Cell Press archive 2005', 'Elsevier open archive join'):
        x = dpl[(dpl.group == 'pure') & (dpl.program == prog)]
        run(x, f'PLACEBO pure age 2 at fake T-3, {prog} only', 'G', weights=('citation-weighted', 'event-weighted'), boot=False, v3w=False)
        x = Bsr[Bsr.program == prog]
        run(x, f'pure age 2 short run (k = 1..2), {prog} only', 'G', weights=('citation-weighted', 'event-weighted'), boot=False, v3w=False)
        ks, b, Vc = event_study(A[A.program == prog], pre=2, post=10)
        es = [dict(k=k, pct=pct(b[i]), lo95=pct(b[i] - 1.96 * math.sqrt(Vc[i, i])), hi95=pct(b[i] + 1.96 * math.sqrt(Vc[i, i]))) for i, k in enumerate(ks)]
        res.append(dict(item='G', set=f'event study, pure age 2, {prog} only, ref k = -1, journal clusters', rows=es)); save()
        log('event study', prog, [(e['k'], round(e['pct'], 1)) for e in es])
except Exception as ex: log('G2 failed', ex); res.append(dict(item='G', error=str(ex)[:300]))
save(); log('done G')
