"""v4 (27 Nov 2026) follow-up after v4_estimates.py and v4_api_checks.py: the meeting-abstract sensitivity.
The API check (api_checks.json, 'swollen_cohorts') shows that several age-2 cohorts in the pure set are mostly conference
abstracts (no reference list, e-/S-pages): HPB 2016, J Thoracic Oncology 2018, Osteoarthritis and Cartilage 2016, Annals of
Physical and Rehabilitation Medicine 2011, International J Surgery 2012; Fertility and Sterility (ASRM abstracts) is large
every year. The panel is aggregated by (journal, publication year), so the abstracts can't be dropped record by record:
this drops those openings. Same model, weights and inference as v4_estimates.py (helpers copied, not imported, so the
main script is not rerun). Also: the age-1 extension and ages 1-2 without them, and without them and Cell Press.
Part 2 (added after the by-program placebos in v4_estimates.py showed real ~ placebo):
 - real minus placebo, pure age 2: the real age-2 cohort over k = 1..2 and the placebo cohort (aged 2 at a fake opening
   T-3, post T-2..T-1), stacked with separate FE, coefficient on tp x real = real minus placebo; journal clusters and a
   score wild-cluster bootstrap by program-date with the placebo slope as a free nuisance regressor (v2 bootstrap logic,
   but the cluster count is taken from the fitted scores, which also fixes the cluster-count error in v4_estimates.py).
 - the flips sets rerun with that bootstrap.
 - Annual Reviews 2023: real minus placebo against matched controls; within-journal W1 placebo (fake opening 2020,
   recent = 2018-2019, older opened = 2014-2017, closed = 2000-2013, citing years to 2022) and real minus placebo.
Run: .venv/bin/python -I scripts/v4_followup.py 2> results/v4_recent/followup.log -> followup.json"""
import sys, os, json, math, warnings
warnings.filterwarnings('ignore')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # published copy: the folder above scripts/
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from v3_common import *  # noqa
import v3_common as V, v2_common as C
OUT4 = os.path.join(ROOT, 'results', 'v4_recent')
C.OUT = OUT4; V.OUT3 = OUT4
res = []
def save(): json.dump(res, open(os.path.join(OUT4, 'followup.json'), 'w'), indent=1, default=float)
def log(*a): print(*a, file=sys.stderr, flush=True)
ct, sz = V.use_panel(clean=True)
st, units = match3()
JN = st.set_index('stack').journal
d = build(st, units); d['ageT'] = d['T'] - d.py; d['journal'] = d['stack'].map(JN)

def renorm(x):
    x = x.copy()
    pre = x[x.k < 0].groupby('stack').y.sum().replace(0, np.nan)
    x['we'] = x['stack'].map(1 / pre).fillna(0) * 1e3
    nb = x[x.treated == 1].drop_duplicates(['stack', 'src', 'py']).groupby('stack').n_articles.sum()
    x['wa'] = x['we'] * x['stack'].map(nb).fillna(0) / 1e3
    return x
def meta(x):
    t = x[x.treated == 1].drop_duplicates(['stack', 'src', 'py'])
    return dict(openings=int(t['stack'].nunique()), papers=int(t.n_articles.sum()), G_pd=int(x[x.treated == 1].pd.nunique()))
def drop_sep(x):
    while True:
        n0 = len(x)
        for fe in ('unit', 's_cy', 's_age'): x = x[x.groupby(fe).y.transform('sum') > 0]
        if len(x) == n0: return x
def run(x, label):
    x = renorm(x); m = meta(x); x = drop_sep(x)
    for wl, w in (('citation-weighted', None), ('event-weighted', 'we'), ('article-weighted', 'wa')):
        xx = x if w is None else x[x[w] > 0]
        r = pooled(xx, f'{label} | {wl} (journal clusters)', weights=w, cluster='src')
        out = dict(set=label, weight=wl, **m, pct=r['pct'], src_lo95=r['lo95'], src_hi95=r['hi95'], mde80_src=pct(2.8016 * r['se']))
        try:
            ci = clustered_inference(xx, f'{label} | {wl}', weights=w, cluster='pd', B=9999)
            out.update({k: ci[k] for k in ('G', 't_lo95', 't_hi95', 'boot_p_zero', 'boot_lo95', 'boot_hi95', 'mde80_crv_t', 'mde80_boot')})
        except Exception as ex: out['boot_error'] = str(ex)[:200]; log('boot failed', ex)
        res.append(out); save()

ABS = {'hpb', 'journal of thoracic oncology', 'osteoarthritis and cartilage', 'annals of physical and rehabilitation medicine',
       'International Journal of Surgery', 'fertility and sterility'}
PART1 = os.environ.get('V4_SKIP_PART1') != '1'   # part 2 was rerun alone after a key-collision bug (results in followup2.json)
P = d[(d.group == 'pure') & d.ageT.isin([1, 2])]
if PART1:
    run(P[~P.journal.isin(ABS)], 'pure age 2, without the 6 abstract-heavy openings')
    run(P[~P.journal.isin(ABS) & (P.program != 'Cell Press archive 2005')], 'pure age 2, without the 6 abstract-heavy openings and Cell Press')
def wall12(r): return (r.program == 'Cell Press archive 2005') or (r.program == 'Elsevier open archive join' and 'embargo 12 months' in str(r.note))
ext = {int(r['stack']) for _, r in st.iterrows() if r.group == 'pure' and wall12(r) and int(r.hi) == int(r['T']) - 2}
uext = [(k, j, tr, lo, (T - 1 if k in ext else hi), T) for (k, j, tr, lo, hi, T) in units if k in ext]
dx = build(st, uext); dx['ageT'] = dx['T'] - dx.py; dx['journal'] = dx['stack'].map(JN)
E = dx[dx.ageT.isin([1, 2]) & ~dx.journal.isin(ABS)]
if PART1:
    run(E, 'EXT ages 1-2 (12-month-wall programs), without the abstract-heavy openings')
    run(E[E.program != 'Cell Press archive 2005'], 'EXT ages 1-2, without the abstract-heavy openings and Cell Press')
log('done')

# ======================= part 2 =======================
res = []
def save(): json.dump(res, open(os.path.join(OUT4, 'followup2.json'), 'w'), indent=1, default=float)
import pyfixest as pf
from scipy import stats
SIX_POINT_WEIGHTS = C.SIX_POINT_WEIGHTS
def _scores(x, xv, nuis, b0, w, cluster):
    x = x.copy(); x['off'] = b0 * x[xv]
    rhs = ' + '.join(nuis) if nuis else '1'
    m = pf.fepois(f'y ~ {rhs} | unit + s_cy + s_age', data=x, offset='off', weights=w)
    dd = m._data.copy(); mu = np.asarray(m.predict(type='response')).ravel()
    ww = dd[w].values.astype(float) if w else np.ones(len(dd))
    dd['wmu'] = ww * mu
    r = pf.feols(f'{xv} ~ {rhs} | unit + s_cy + s_age', data=dd, weights='wmu', fixef_rm='none')
    xt = np.asarray(r.resid()).ravel()
    return pd.Series(ww * xt * (dd.y.values - mu)).groupby(dd[cluster].values).sum().values
def _p(x, xv, nuis, b0, w, cluster, B=9999, seed=7):
    S = _scores(x, xv, nuis, b0, w, cluster); G = len(S)
    t = S.sum() / math.sqrt((S ** 2).sum())
    Wb = SIX_POINT_WEIGHTS[np.random.default_rng(seed).integers(0, 6, size=(B, G))]
    Sb = Wb * S; tb = Sb.sum(1) / np.sqrt((Sb ** 2).sum(1))
    return float((np.abs(tb) >= abs(t)).mean()), G
def boot(x, xv='tp', nuis=(), w=None, cluster='pd', B=9999):
    """point estimate + journal-clustered and pd-CRV1 SEs + score wild-cluster bootstrap p and test-inversion CI."""
    rhs = ' + '.join([xv] + list(nuis))
    out = {}
    for cl in ('src', cluster):
        if x[cl].nunique() < 2: out[cl] = dict(b=float('nan'), se=float('nan'), G=1); continue   # one cluster: CRV1 undefined
        m = pf.fepois(f'y ~ {rhs} | unit + s_cy + s_age', data=x, vcov={'CRV1': cl}, weights=w)
        b, se = float(m.coef()[xv]), float(m.se()[xv]); G = int(m._data[cl].nunique())
        out[cl] = dict(b=b, se=se, G=G)
    b = out['src']['b']; r = dict(pct=pct(b), src_lo95=pct(b - 1.96 * out['src']['se']), src_hi95=pct(b + 1.96 * out['src']['se']),
                                  mde80_src=pct(2.8016 * out['src']['se']), G_src=out['src']['G'])
    G = out[cluster]['G']; sp = out[cluster]['se']
    if G >= 3:
        tc, t8 = stats.t.ppf(0.975, G - 1), stats.t.ppf(0.80, G - 1)
        r.update(G_pd_fit=G, t_lo95=pct(b - tc * sp), t_hi95=pct(b + tc * sp), mde80_crv_t=pct((tc + t8) * sp))
    if G >= 6:
        p0, Gs = _p(x, xv, nuis, 0.0, w, cluster, B)
        def cross(step):
            inside, outv = b, b + step
            for _ in range(40):
                if _p(x, xv, nuis, outv, w, cluster, B)[0] < 0.05: break
                inside, outv = outv, outv + step
            else: return float('nan')
            for _ in range(10):
                mid = (inside + outv) / 2
                if _p(x, xv, nuis, mid, w, cluster, B)[0] >= 0.05: inside = mid
                else: outv = mid
            return (inside + outv) / 2
        lo, hi = cross(-max(sp, out['src']['se'], 0.005)), cross(max(sp, out['src']['se'], 0.005))
        r.update(boot_p_zero=p0, G_boot=Gs, boot_lo95=pct(lo), boot_hi95=pct(hi),
                 mde80_boot=pct(2.8016 * (hi - lo) / (2 * 1.96)) if not (math.isnan(lo) or math.isnan(hi)) else None)
    return r
def show(lab, r): log(f"{lab:85s} {r['pct']:+6.1f}% journal [{r['src_lo95']:+.1f}, {r['src_hi95']:+.1f}]"
                      + (f"  pd-t [{r['t_lo95']:+.1f}, {r['t_hi95']:+.1f}]" if 't_lo95' in r else '')
                      + (f"  boot [{r['boot_lo95']:+.1f}, {r['boot_hi95']:+.1f}] p {r['boot_p_zero']:.2f}" if 'boot_lo95' in r else '')
                      + f"  MDE journal {r['mde80_src']:.1f}" + (f" boot {r['mde80_boot']:.1f}" if r.get('mde80_boot') else ''))
def run2(x, lab, item, xv='tp', nuis=(), weights=('citation-weighted', 'event-weighted')):
    x = renorm(x); m = meta(x); x = drop_sep(x)
    for wl, w in (('citation-weighted', None), ('event-weighted', 'we'), ('article-weighted', 'wa')):
        if wl not in weights: continue
        xx = x if w is None else x[x[w] > 0]
        try: r = boot(xx, xv, nuis, w)
        except Exception as ex: log('FAILED', lab, wl, ex); res.append(dict(item=item, set=lab, weight=wl, error=str(ex)[:200])); continue
        show(f'{lab} | {wl}', r); res.append(dict(item=item, set=lab, weight=wl, **m, **r)); save()
def tag(x, p):
    x = x.copy()
    for c in ('unit', 's_cy', 's_age'): x[c] = p + x[c].astype(str)
    return x
def real_vs_placebo(real, plac):
    """real and placebo panels with separate FE; tp_any = treated x post in either, tp = treated x post in the real one."""
    a = tag(real, 'R_').assign(is_real=1); b = tag(plac, 'P_').assign(is_real=0)
    x = pd.concat([a, b], ignore_index=True)
    x['tp_any'] = x.tp; x['tp'] = x.tp * x.is_real
    return x

# --- pure age 2: real (k = 1..2) minus placebo (aged 2 at fake T-3) ---
dsr = build(st, units, pre=5, post=2); dsr['ageT'] = dsr['T'] - dsr.py
R = dsr[(dsr.group == 'pure') & (dsr.ageT == 2)]
a2 = set(R['stack'].unique())
upl = [(k, j, tr, T - 5, T - 5, T - 3) for (k, j, tr, lo, hi, T) in units if k in a2 and lo <= T - 5]
PL = build(st, upl, pre=5, post=2); PL = PL[PL.group == 'pure']
both = set(PL['stack'].unique())       # openings with both a real and a placebo cohort
run2(R[R['stack'].isin(both)], 'RVP pure age 2, real short run (k = 1..2), openings with a placebo cohort', 'RVP')
run2(PL, 'RVP pure placebo (cohort aged 2 at fake T-3, post T-2..T-1)', 'RVP')
run2(real_vs_placebo(R[R['stack'].isin(both)], PL), 'RVP pure age 2, REAL MINUS PLACEBO', 'RVP', xv='tp', nuis=('tp_any',))
for prog in ('Cell Press archive 2005', 'Elsevier open archive join'):
    run2(real_vs_placebo(R[R['stack'].isin(both) & (R.program == prog)], PL[PL.program == prog]), f'RVP {prog}, REAL MINUS PLACEBO', 'RVP', xv='tp', nuis=('tp_any',))

# --- flips rerun with the fixed bootstrap (v4_estimates.py section E) ---
d['ar'] = np.where(d.program.str.startswith('Annual Reviews S2O 2023'), 'ar2023', np.where(d.program.str.startswith('Annual Reviews S2O pilot'), 'arpilot', ''))
F = d[(d.group != 'pure') & d.ageT.isin([1, 2])]
run2(F[(F.ar == '') & (F.platform_move == 0)], 'FLIPS other flips / front list, no platform move, ages 1-2', 'E2', weights=('citation-weighted', 'event-weighted', 'article-weighted'))
run2(F[(F.ar == '')], 'FLIPS other flips incl. platform moves, ages 1-2', 'E2', weights=('citation-weighted', 'event-weighted', 'article-weighted'))
run2(F[F.platform_move == 0], 'FLIPS all (Annual Reviews + other), no platform move, ages 1-2', 'E2', weights=('citation-weighted', 'event-weighted', 'article-weighted'))

# --- Annual Reviews 2023: real minus placebo against matched controls (journal clusters; one date, so no pd bootstrap) ---
AR = st[st.program.str.startswith('Annual Reviews S2O 2023')]; ars = set(AR['stack'])
RA = F[F.ar == 'ar2023']
upa = [(k, j, tr, max(lo, T - 5), T - 4, T - 3) for (k, j, tr, lo, hi, T) in units if k in ars and lo <= T - 5]
PA = build(st, upa, pre=5, post=2)
bA = set(PA['stack'].unique())
run2(real_vs_placebo(RA[RA['stack'].isin(bA)], PA), 'RVP AR 2023 ages 1-2 vs matched controls, REAL MINUS PLACEBO (fake 2020)', 'RVP-AR', xv='tp', nuis=('tp_any',))

# --- Annual Reviews 2023 within journal (W1) and its placebo ---
def within_ar(Tfake=None, cy_max=2025):
    frames = []
    for _, r in AR.iterrows():
        s, T, lo, hi = int(r.treated), int(r['T']), int(r.lo), int(r.hi)
        if Tfake: T = Tfake; hi = Tfake - 1
        z = sz[(sz.src == s) & (sz.n_articles > 0) & (sz.py.between(lo, hi) | sz.py.between(2000, 2013))].copy()
        z['opened'] = z.py.between(lo, hi).astype(int)
        if z.opened.sum() == 0 or (1 - z.opened).sum() == 0: continue
        a = z.merge(pd.DataFrame({'cy': range(max(1995, T - 5), min(cy_max, T + 10) + 1)}), how='cross')
        a = a.merge(ct[ct.src == s][['py', 'cy', 'cites']], on=['py', 'cy'], how='left').fillna({'cites': 0})
        a['stack'] = int(r['stack']); a['T'] = T; frames.append(a)
    x = pd.concat(frames, ignore_index=True)
    x['k'] = x.cy - x['T']; x = x[x.k != 0].copy(); x['age'] = (x.cy - x.py).clip(upper=80); x['y'] = x.cites
    x['post'] = (x.k >= 1).astype(int); x['recent'] = ((x.opened == 1) & (x['T'] - x.py <= 2)).astype(int)
    x['tp'] = x.recent * x.post; x['tp_older'] = (x.opened - x.recent) * x.post
    x['unit'] = x['stack'].astype(str) + '_' + x.py.astype(str)
    x['s_cy'] = x['stack'].astype(str) + '_' + x.cy.astype(str); x['s_age'] = x['stack'].astype(str) + '_' + x.age.astype(str)
    x['pd'] = 'ar2023'
    return x
def fitw(x, lab, terms):
    m = pf.fepois('y ~ ' + ' + '.join(terms) + ' | unit + s_cy + s_age', data=x, vcov={'CRV1': 'src'})
    co, se = m.coef(), m.se()
    o = dict(item='W1', set=lab, journals=int(x.src.nunique()),
             **{t: dict(pct=pct(co[t]), lo95=pct(co[t] - 1.96 * se[t]), hi95=pct(co[t] + 1.96 * se[t]), mde80_src=pct(2.8016 * se[t])) for t in terms})
    log(lab, {t: (round(o[t]['pct'], 1), round(o[t]['lo95'], 1), round(o[t]['hi95'], 1)) for t in terms}); res.append(o); save()
WR = within_ar(); WP = within_ar(Tfake=2020, cy_max=2022)
fitw(WR, 'W1 real: AR 2023 volumes aged 1-2 (tp) and 3-9 (tp_older) vs closed 2000-2013, same journal', ['tp', 'tp_older'])
fitw(WP, 'W1 placebo: fake opening 2020, volumes 2018-2019 (tp) and 2014-2017 (tp_older) vs closed 2000-2013, citing years to 2022', ['tp', 'tp_older'])
x = pd.concat([tag(WR, 'R_').assign(is_real=1), tag(WP, 'P_').assign(is_real=0)], ignore_index=True)
for c in ('tp', 'tp_older'): x[c + '_any'] = x[c]; x[c] = x[c] * x.is_real
fitw(x, 'W1 REAL MINUS PLACEBO (tp = recent volumes, tp_older = older opened volumes)', ['tp', 'tp_older', 'tp_any', 'tp_older_any'])
log('done part 2')
