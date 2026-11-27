"""v3 (22 Nov 2026): everything except the headline estimands, on the v3 pure set and the one Q12 panel (cleaned).
 counts; event study (k -5..+10, ref -1, journal clusters) and placebo T-3; chart 1 raw balanced series (-5..+8, same method
 as field-notes/charts/backfile_raw_balanced.json) + share of year -1 citations from papers published in the 5 years before
 opening; maths split; age at opening subgroups (1-5, 6-15, 16-40, >40 years); two-date-source subset; citing side
 (journal articles each counted once; and DOI-record lists) and the split of the gain by citing type (journal articles vs
 repository-only citers), with and without Cell Press; provenance shares by year; fix-3 diagnostics; within-journal
 sources affected? Out: results/v3/extras.json, event_study_v3.tsv, chart1_raw_balanced.json, provenance_by_year_v3.tsv"""
import sys, warnings; warnings.filterwarnings('ignore'); sys.path.insert(0, 'scripts')
from v3_common import *
import v3_common as V, v2_common as C
ct, sz = V.use_panel(clean=True)
st, units = match3()
d = add_weights(build(st, units, outcomes=tuple(OUTCOMES)))
P = pure(d); ps = st[st.group == 'pure'].copy()
res = []
def runw(x, lab, item, weights=('citation-weighted', 'event-weighted', 'article-weighted'), cluster='src', **kw):
    for wl in weights:
        w = {'citation-weighted': None, 'event-weighted': 'we', 'article-weighted': 'wa'}[wl]
        xx = x if w is None else x[x[w] > 0]
        res.append(dict(item=item, set=lab, weight=wl, **kw, **pooled(xx, f'{lab} | {wl}', weights=w, cluster=cluster)))
# counts
cy = ps['T'] - ps.hi
res.append(dict(item='counts', openings=len(ps), journals=int(ps.treated.nunique()), papers=int(ps.treated_n.sum()), G=int(ps.pd.nunique()),
                T_min=int(ps['T'].min()), T_max=int(ps['T'].max()), cohort_py_min=int(ps.lo.min()), cohort_py_max=int(ps.hi.max()),
                median_T_minus_hi=float(cy.median()), by_program=ps.groupby('program').agg(n=('stack', 'size'), papers=('treated_n', 'sum')).to_dict('index'),
                five_controls=int((ps.controls.str.split().str.len() == 5).sum()), distinct_controls=len({c for cs in ps.controls for c in cs.split()}),
                two_date_sources=int((ps.n_date_sources >= 2).sum()),
                all_v3_openings=int((st.platform_move == 0).sum()), status=st.v3_status.value_counts().to_dict()))
dump3(res, 'extras.json')
# event study
ks, b, Vc = event_study(P)
es = [dict(k=k, pct=pct(b[i]), lo95=pct(b[i] - 1.96 * math.sqrt(Vc[i, i])), hi95=pct(b[i] + 1.96 * math.sqrt(Vc[i, i]))) for i, k in enumerate(ks)]
pd.DataFrame(es).to_csv(os.path.join(OUT3, 'event_study_v3.tsv'), sep='\t', index=False)
pl = P[P.k < 0].copy(); pl['tp'] = pl.treated * (pl.k >= -3).astype(int)
res.append(dict(item='placebo', set='PURE v3 placebo T-3', **pooled(pl, 'PURE v3 | placebo T-3')))
# chart 1 raw balanced
bal = ps[ps['T'] + 8 <= 2025]
rows = []
for _, r in bal.iterrows():
    for g, srcs in (('opened', [r.treated]), ('control', [int(x) for x in str(r.controls).split()])):
        for s in srcs: rows.append((r['stack'], g, s, r['T'], r.lo, r.hi))
u = pd.DataFrame(rows, columns=['stack', 'g', 'src', 'T', 'lo', 'hi'])
a = u.merge(sz, on='src'); a = a[a.py.between(a.lo, a.hi)]
den = a.groupby('g').n_articles.sum()
c = u.merge(ct, on='src'); c = c[c.py.between(c.lo, c.hi)]; c['k'] = c.cy - c['T']
num = c[c.k.between(-5, 8)].groupby(['g', 'k']).cites.sum().unstack(0)
rate = num / den; idx = (rate / rate.loc[-1] * 100).round(1)
m1 = c[c.k == -1]; recent = m1[m1.py >= m1['T'] - 5]
sh = (recent.groupby('g').cites.sum() / m1.groupby('g').cites.sum()).round(3)
chart = dict(k=list(range(-5, 9)), opened=idx.opened.tolist(), control=idx.control.tolist(), n_openings=int(len(bal)),
             articles=int(den['opened']), treated_n_sum=int(bal.treated_n.sum()),
             share_minus1_cites_from_papers_published_T_minus_5_to_T_minus_1=dict(opened=float(sh['opened']), control=float(sh['control'])),
             note='per group: sum of citations in event year k / sum of articles in the cohort years, indexed to k = -1; openings with T + 8 <= 2025; v3 pure set, Q12 panel cleaned')
json.dump(chart, open(os.path.join(OUT3, 'chart1_raw_balanced.json'), 'w'), indent=1)
res.append(dict(item='chart1', **chart))
dump3(res, 'extras.json')
# maths split
d['tfield'] = d['stack'].map(st.set_index('stack').treated.map(field)); P = pure(d)
MP = ['Elsevier maths open archive 2012', 'AMS back file 2010']
mm = P.program.isin(MP) | (P.tfield == 'Mathematics')
tr = P[P.treated == 1].groupby('stack').agg(prog=('program', 'first'), f=('tfield', 'first'), n=('treated_n', 'first'))
res.append(dict(item='maths shares', maths_programs=int(tr.prog.isin(MP).sum()), maths_programs_papers=int(tr[tr.prog.isin(MP)].n.sum()),
                maths_field=int((tr.f == 'Mathematics').sum()), programs_or_field=int((tr.prog.isin(MP) | (tr.f == 'Mathematics')).sum()),
                programs_or_field_papers=int(tr[tr.prog.isin(MP) | (tr.f == 'Mathematics')].n.sum()), openings=len(tr), papers=int(tr.n.sum())))
x = P[~mm]
r = clustered_inference(x, 'PURE v3, no maths programs or maths journals | citation-weighted', cluster='pd', B=4999)
res.append(dict(item='maths', set='PURE v3 no maths programs or maths journals', weight='citation-weighted', **r))
runw(x, 'PURE v3 no maths programs or maths journals', 'maths', weights=('event-weighted', 'article-weighted'), cluster='pd')
runw(P[P.program.isin(MP)], 'PURE v3 two maths programs only', 'maths')
runw(P[P.tfield == 'Mathematics'], 'PURE v3 maths-field journals only', 'maths')
dump3(res, 'extras.json')
# age at opening
P = P.assign(ageT=P['T'] - P.py)
for lo_, hi_ in ((1, 5), (6, 15), (16, 40), (41, 999)):
    x = P[P.ageT.between(lo_, hi_)]
    tre = x[x.treated == 1].drop_duplicates(['stack', 'src', 'py'])
    runw(x, f'PURE v3 papers {lo_}-{hi_} years old at opening', 'age', openings=int(tre['stack'].nunique()),
         papers=int(tre.n_articles.sum()), share_papers=float(tre.n_articles.sum() / P[P.treated == 1].drop_duplicates(['stack', 'src', 'py']).n_articles.sum()))
# two date sources
runw(P[P.n_date_sources >= 2], 'PURE v3 openings with two date sources', 'two sources', openings=int(P[P.n_date_sources >= 2]['stack'].nunique()))
dump3(res, 'extras.json')
# citing side
for o, lab in (('cites_ja', 'journal articles citing, each counted once'), ('cites_ja_cr', 'journal articles citing once, list filed on the DOI record'),
               ('cites_repo_only', 'repository-only citers')):
    for nm, x in (('PURE v3', P), ('PURE v3 without Cell Press', P[P.program != 'Cell Press archive 2005'])):
        xx = add_weights(x.assign(y=x[o]).copy())
        runw(xx, f'{nm} | {lab}', 'citing', outcome=o)
for nm, x in (('PURE v3', P), ('PURE v3 without Cell Press', P[P.program != 'Cell Press archive 2005'])):
    xx = x.assign(y=x.cites - x.cites_ja - x.cites_repo_only)
    res.append(dict(item='citing', set=f'{nm} | other citers (not journal articles, not repository-only)', weight='citation-weighted', outcome='other', **pooled(xx, f'{nm} other citers')))
    res.append(dict(item='citing', set=nm, note='share of treated post-period citations by type',
                    shares={o: float(x[(x.treated == 1) & (x.k >= 1)][o].sum() / x[(x.treated == 1) & (x.k >= 1)].cites.sum()) for o in ('cites_ja', 'cites_repo_only', 'cites_ja_cr')}))
dump3(res, 'extras.json')
# provenance by citing year (pure v3 cohort cells)
cells = P[['stack', 'src', 'py', 'treated']].drop_duplicates()[['src', 'py', 'treated']].drop_duplicates()
pool = ct.merge(cells, on=['src', 'py']).groupby(['treated', 'cy'])[OUTCOMES].sum().reset_index()
for o in ('cites_ja', 'cites_repo_only', 'cites_ja_cr'): pool['share_' + o] = pool[o] / pool.cites
pool['pool'] = np.where(pool.treated == 1, 'treated', 'control')
pool[pool.cy >= 1995].drop(columns='treated').to_csv(os.path.join(OUT3, 'provenance_by_year_v3.tsv'), sep='\t', index=False)
# fix 3 diagnostics: cohort-window share of records not carrying a home prefix, treated and controls, before cleaning
R = V.KEEPRECS
diag = []
for _, r in st.iterrows():
    for s, role in [(r.treated, 'treated')] + [(int(c), 'control') for c in r.controls.split()]:
        x = R[(R.src == s) & R.py.between(r.lo, r.hi)]
        n = x.n_articles.sum()
        if n == 0: continue
        nh = x[x.cls != 'home'].n_articles.sum(); nd = x[~x.keep].n_articles.sum()
        diag.append(dict(stack=r['stack'], group=r.group, role=role, src=s, journal=host(s) if False else C.SRC.get(s, {}).get('display_name', ''), n=int(n),
                         share_not_home=float(nh / n), dropped=int(nd), jstor=int(x[x.cls == 'jstor'].n_articles.sum())))
dg = pd.DataFrame(diag); dg.to_csv(os.path.join(OUT3, 'fix3_record_diagnostics.tsv'), sep='\t', index=False)
f = dg[dg.share_not_home > 0.2]
res.append(dict(item='fix3', sources_over_20pct_not_home=f.groupby('role').src.nunique().to_dict(),
                treated_over_20=f[f.role == 'treated'][['journal', 'n', 'share_not_home', 'dropped', 'jstor']].to_dict('records'),
                dropped_records_treated=int(dg[dg.role == 'treated'].drop_duplicates(['stack', 'src']).dropped.sum()),
                dropped_records_controls=int(dg[dg.role == 'control'].drop_duplicates(['stack', 'src']).dropped.sum())))
# within-journal programs affected by the record cleaning?
wj = []
for e in V.EV3:
    if e['program'] in ('Annual Reviews S2O 2023 (previous nine volumes)', 'Royal Society archive 2011'):
        x = R[R.src == int(e['source'])]
        wj.append(dict(journal=e['journal'], program=e['program'], records=int(x.n_articles.sum()), dropped=int(x[~x.keep].n_articles.sum())))
res.append(dict(item='within-journal check', dropped_total=sum(w['dropped'] for w in wj), rows=wj))
dump3(res, 'extras.json')
print('done', file=sys.stderr)
