"""v2 shared code (22 Nov 2026). Replicates estimate.py's matching, panel build and PPML without writing any v1 file,
and adds: a second matching profile (T-8..T-4 only), panels from the v2 Q10 extract (arXiv split, citing-side outcomes),
program-date clusters, article weights, a score wild-cluster bootstrap for PPML with test-inversion CIs,
and event-study linear combinations (re-referencing, pre-trend extrapolation, relative-magnitude bounds).
Import from the workspace root: .venv/bin/python -I scripts/v2_xxx.py (each script chdirs to the workspace)."""
import csv, json, math, collections, os, sys
import numpy as np, pandas as pd, pyfixest as pf
from scipy import stats

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
OUT = os.path.join(ROOT, 'results', 'v2')
os.makedirs(OUT, exist_ok=True)
csv.field_size_limit(10**9)
def rd(p): return list(csv.DictReader(open(p), delimiter='\t', quoting=csv.QUOTE_NONE))
LAST_CY, NCTRL = 2025, 5

# ---- v1 inputs (read only) ----
panel = pd.read_csv('data/q08_panel.csv', dtype={'src': 'int64', 'py': 'int64', 'green': 'int64'})
panel['cy'] = panel['cy'].astype('Int64')
sizes = panel.groupby(['src', 'py', 'green'], as_index=False)[['n_articles', 'n_oa_pub_now']].first()
cit = panel.dropna(subset=['cy']).astype({'cy': 'int64'})
events = rd('results/final_events.tsv')
cands = collections.defaultdict(list)
for c in rd('data/control_candidates.tsv'): cands[(c['treated'], c['T'])].append(int(c['control']))
_q3 = json.load(open('data/q03_sources.json'))
SRC = {int(r[0]): dict(zip(_q3['cols'], r)) for r in _q3['rows']}
def host(s): return (SRC.get(int(s), {}).get('host_organization_name') or '')
def field(s): return (SRC.get(int(s), {}).get('field') or '')

FLIPS = ('Annual Reviews S2O 2023 (previous nine volumes)', 'Annual Reviews S2O pilot (all back volumes)', 'single-journal opening (flip)')
AR = FLIPS[:2]

jc = cit.groupby(['src', 'py', 'cy'])['cites'].sum()
jn = sizes.groupby(['src', 'py'])['n_articles'].sum()

def pre_profile(src, lo, hi, T, mode='v1'):
    """v1: level over T-5..T-1, growth (T-2..T-1 vs T-5..T-4). early: level over T-8..T-4, growth (T-5..T-4 vs T-8..T-7)."""
    try: n = jn.loc[src]
    except KeyError: return None
    n = n[(n.index >= lo) & (n.index <= min(hi, T - 1))].sum()
    if n < 30: return None
    try: c = jc.loc[src]
    except KeyError: return None
    c = c[(c.index.get_level_values('py') >= lo) & (c.index.get_level_values('py') <= min(hi, T - 1))]
    by = c.groupby(level='cy').sum()
    if mode == 'v1':
        early = by.reindex(range(T - 5, T - 3), fill_value=0).sum(); late = by.reindex(range(T - 2, T), fill_value=0).sum()
        lvl = (early + by.reindex([T - 3], fill_value=0).sum() + late) / n
    else:
        early = by.reindex(range(T - 8, T - 6), fill_value=0).sum(); late = by.reindex(range(T - 5, T - 3), fill_value=0).sum()
        lvl = (early + by.reindex([T - 6], fill_value=0).sum() + late) / n
    return dict(n=n, lvl=lvl, gr=math.log((late + 1) / (early + 1)))

def match(mode='v1', cand_filter=None, keep=None):
    """Returns (stacks DataFrame, units list). keep(e) -> bool restricts events; cand_filter(control_id) -> bool."""
    stacks, units = [], []
    for k, e in enumerate(events):
        if keep is not None and not keep(e): continue
        s, T, lo, hi = int(e['source']), int(e['T']), int(e['cohort_from']), int(e['cohort_to'])
        hi = min(hi, T - 1)
        if T + 1 > LAST_CY: continue
        tp = pre_profile(s, lo, hi, T, mode)
        if tp is None or tp['lvl'] == 0: continue
        scored = []
        for c in cands[(e['source'], e['T'])]:
            if cand_filter is not None and not cand_filter(c): continue
            cp = pre_profile(c, lo, hi, T, mode)
            if cp is None or cp['lvl'] == 0: continue
            d = abs(math.log(cp['lvl']) - math.log(tp['lvl'])) + abs(cp['gr'] - tp['gr']) + 0.25 * abs(math.log(cp['n'] / tp['n']))
            scored.append((d, c))
        scored.sort()
        ctrls = [c for _, c in scored[:NCTRL]]
        if len(ctrls) < 2: continue
        stacks.append(dict(stack=k, treated=s, journal=e['journal'], program=e['program'], T=T, lo=lo, hi=hi,
                           n_date_sources=int(e['n_date_sources']), flip=int(e['flip']), note=e['note'],
                           treated_n=int(tp['n']), controls=' '.join(map(str, ctrls)),
                           mean_match_dist=round(sum(d for d, _ in scored[:NCTRL]) / len(ctrls), 3)))
        for j, tr in [(s, 1)] + [(c, 0) for c in ctrls]:
            units.append((k, j, tr, lo, hi, T))
    st = pd.DataFrame(stacks)
    st['platform_move'] = st.note.fillna('').str.contains('platform move').astype(int)
    st['pd'] = np.where(st.program.str.startswith('single-journal'), 'single_' + st.treated.astype(str), st.program + '|' + st['T'].astype(str))
    st['group'] = np.select([st.program.isin(AR), st.program == FLIPS[2]], ['Annual Reviews S2O', 'other flips'], 'pure')
    return st, units

def build(st, units, cy_df=None, sz_df=None, outcomes=('cites',), pre=5, post=10, split=None):
    """Stacked panel. cy_df: src, py, [g/axy], cy, outcome cols; sz_df: src, py, [..], n_articles.
    split='arxiv' -> unit split by ax = arXiv copy posted before T (needs axy column)."""
    cy_df = cit if cy_df is None else cy_df
    sz_df = sizes if sz_df is None else sz_df
    u = pd.DataFrame(units, columns=['stack', 'src', 'treated', 'lo', 'hi', 'T'])
    srcs = set(u.src)
    cyd = cy_df[cy_df.src.isin(srcs)]; szd = sz_df[sz_df.src.isin(srcs)]
    frames = []
    for (k, T), g in u.groupby(['stack', 'T']):
        lo, hi = g.lo.iloc[0], g.hi.iloc[0]
        a = szd[szd.src.isin(g.src) & szd.py.between(lo, hi)]
        c = cyd[cyd.src.isin(g.src) & cyd.py.between(lo, hi) & cyd.cy.between(max(1995, T - pre), min(LAST_CY, T + post))]
        if split == 'arxiv':
            a = a.assign(ax=((a.axy > 0) & (a.axy < T)).astype(int)); c = c.assign(ax=((c.axy > 0) & (c.axy < T)).astype(int))
            keys = ['src', 'py', 'ax']
        else:
            keys = ['src', 'py']
        a = a.groupby(keys, as_index=False).n_articles.sum(); a = a[a.n_articles > 0]
        c = c.groupby(keys + ['cy'], as_index=False)[list(outcomes)].sum()
        a = a.merge(g[['src', 'treated']], on='src')
        a = a.merge(pd.DataFrame({'cy': range(max(1995, T - pre), min(LAST_CY, T + post) + 1)}), how='cross')
        a = a.merge(c, on=keys + ['cy'], how='left').fillna({o: 0 for o in outcomes})
        a['stack'] = k; a['T'] = T
        frames.append(a)
    d = pd.concat(frames, ignore_index=True)
    d['k'] = d.cy - d['T']; d['age'] = (d.cy - d.py).clip(upper=80)
    d = d[d.k != 0].copy()
    d['y'] = d[outcomes[0]]
    d['post'] = (d.k >= 1).astype(int); d['tp'] = d.treated * d.post
    d['unit'] = d['stack'].astype(str) + '_' + d.src.astype(str) + '_' + d.py.astype(str) + (('_' + d.ax.astype(str)) if split == 'arxiv' else '')
    d['s_cy'] = d['stack'].astype(str) + '_' + d.cy.astype(str); d['s_age'] = d['stack'].astype(str) + '_' + d.age.astype(str)
    sti = st.set_index('stack')
    for col in ('program', 'pd', 'group', 'platform_move', 'n_date_sources', 'treated_n'):
        d[col] = d['stack'].map(sti[col])
    return d

def add_weights(d):
    """we = each event equal (v1 rule: 1 / stack pre-period citations); wa = articles opened (treated_n / stack pre-period citations)."""
    pre = d[d.k < 0].groupby('stack').y.sum().replace(0, np.nan)
    d['we'] = d['stack'].map(1 / pre).fillna(0) * 1e3
    d['wa'] = d['we'] * d['treated_n'] / 1e3
    return d

def pct(b): return 100 * (math.exp(b) - 1)

def pooled(d, label, weights=None, cluster='src', quiet=False):
    try:
        m = pf.fepois('y ~ tp | unit + s_cy + s_age', data=d, vcov={'CRV1': cluster}, weights=weights)
        b, se = float(m.coef()['tp']), float(m.se()['tp'])
    except Exception as ex:
        print('FAILED', label, ex, file=sys.stderr); return dict(label=label, error=str(ex)[:200])
    G = int(d[cluster].nunique())
    r = dict(label=label, b=b, se=se, pct=pct(b), lo95=pct(b - 1.96 * se), hi95=pct(b + 1.96 * se),
             n_obs=int(m._N), n_stacks=int(d['stack'].nunique()), n_treated_journals=int(d[d.treated == 1].src.nunique()),
             treated_articles=int(d[d.treated == 1].groupby('stack').treated_n.first().sum()), cluster=cluster, G=G)
    if not quiet: print(f"{label:62s} {r['pct']:+6.1f}% [{r['lo95']:+.1f}, {r['hi95']:+.1f}]  stacks {r['n_stacks']}", file=sys.stderr, flush=True)
    return r

def event_study(d, pre=5, post=10, omit=(-1,), cluster='src', weights=None):
    """Returns (ks, b vector, vcov matrix) for k in -pre..post except 0 and omitted."""
    d = d.copy(); ks = []
    for k in range(-pre, post + 1):
        if k == 0 or k in omit: continue
        col = f'e{k + 50}'
        d[col] = ((d.k == k) & (d.treated == 1)).astype(int)
        if d[col].sum() > 0: ks.append(k)
    terms = [f'e{k + 50}' for k in ks]
    m = pf.fepois('y ~ ' + ' + '.join(terms) + ' | unit + s_cy + s_age', data=d, vcov={'CRV1': cluster}, weights=weights)
    co = m.coef(); V = pd.DataFrame(m._vcov, index=co.index, columns=co.index)
    return ks, co[terms].values, V.loc[terms, terms].values

# ---------- score wild-cluster bootstrap for PPML with high-dimensional FE ----------
class PPMLData:
    """Restricted PPML fits (slope fixed at b0 through an offset) via pyfixest; x residualized on the FE with weights w*mu0
    (feols residuals, no singleton removal); per-cluster scores for the score bootstrap."""
    def __init__(self, d, cluster, weights=None):
        self.d = d.copy(); self.cluster = cluster; self.weights = weights
        self.G = int(self.d[cluster].nunique())
    def scores(self, b0):
        d = self.d; d['off'] = b0 * d.tp
        m = pf.fepois('y ~ 1 | unit + s_cy + s_age', data=d, offset='off', weights=self.weights)
        dd = m._data.copy(); mu = np.asarray(m.predict(type='response')).ravel()
        w = dd[self.weights].values.astype(float) if self.weights else np.ones(len(dd))
        dd['wmu'] = w * mu
        r = pf.feols('tp ~ 1 | unit + s_cy + s_age', data=dd, weights='wmu', fixef_rm='none')
        xt = np.asarray(r.resid()).ravel()
        s = w * xt * (dd.y.values - mu)
        S = pd.Series(s).groupby(dd[self.cluster].values).sum()
        return S.values, float((w * mu * xt * xt).sum())

SIX_POINT_WEIGHTS = np.array([-math.sqrt(1.5), -1, -math.sqrt(.5), math.sqrt(.5), 1, math.sqrt(1.5)])
def score_boot_p(D, b0, B=9999, seed=7):
    S, H = D.scores(b0)
    t = S.sum() / math.sqrt((S ** 2).sum())
    rng = np.random.default_rng(seed)
    W = SIX_POINT_WEIGHTS[rng.integers(0, 6, size=(B, D.G))]
    Sb = W * S
    tb = Sb.sum(1) / np.sqrt((Sb ** 2).sum(1))
    return float((np.abs(tb) >= abs(t)).mean()), t

def boot_ci(D, bhat, se_guess, alpha=0.05, B=9999):
    """Test-inversion CI: bisection for the b0 where the bootstrap p crosses alpha, each side."""
    def crossing(inside, step):
        out = inside + step
        for _ in range(40):
            if score_boot_p(D, out, B)[0] < alpha: break
            inside, out = out, out + step
        else: return float('nan')
        for _ in range(10):
            mid = (inside + out) / 2
            if score_boot_p(D, mid, B)[0] >= alpha: inside = mid
            else: out = mid
        return (inside + out) / 2
    return crossing(bhat, -se_guess), crossing(bhat, se_guess)

def clustered_inference(d, label, weights=None, cluster='pd', B=9999):
    """Point estimate (pyfixest), CRV1 by program-date with t(G-1), score wild-cluster bootstrap p and CI, MDE at 80% power."""
    r = pooled(d, label, weights=weights, cluster=cluster)
    if 'error' in r: return r
    G = r['G']; b, se = r['b'], r['se']
    tc = stats.t.ppf(0.975, G - 1); tp80 = stats.t.ppf(0.80, G - 1)
    r.update(t_lo95=pct(b - tc * se), t_hi95=pct(b + tc * se))
    D = PPMLData(d, cluster, weights)
    p0, t0 = score_boot_p(D, 0.0, B)
    lo, hi = boot_ci(D, b, max(se, 0.005), B=B)
    r.update(boot_p_zero=p0, boot_lo95=pct(lo), boot_hi95=pct(hi))
    se_boot = (hi - lo) / (2 * 1.96) if not (math.isnan(lo) or math.isnan(hi)) else float('nan')
    r.update(mde80_crv_t=pct((tc + tp80) * se), mde80_boot=pct((1.96 + 0.8416) * se_boot) if not math.isnan(se_boot) else None)
    print(f"   {cluster} G={G}: t-CI [{r['t_lo95']:+.1f}, {r['t_hi95']:+.1f}]  boot p0={p0:.3f} CI [{r['boot_lo95']:+.1f}, {r['boot_hi95']:+.1f}]  MDE80 {r['mde80_crv_t']:.1f}% / {r['mde80_boot']}", file=sys.stderr, flush=True)
    return r

def dump(obj, name):
    json.dump(obj, open(os.path.join(OUT, name), 'w'), indent=1, default=float)
