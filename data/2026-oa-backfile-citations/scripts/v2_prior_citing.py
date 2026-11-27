"""v2 items 5 and 7 (22 Nov 2026), on the v2 Q10 extract (data/v2_q10_panel.csv; same sources as Q08, snapshot 22 Nov).
Matching and stacks are v1's (from Q08), so differences come from the outcome or the split only.
 7a: outcome variants: all served edges (22 Nov snapshot, compare with v1's 21 Nov Q08 numbers), deduplicated journal
     articles/reviews only, edges with Crossref provenance, both.
 7b: citation provenance by citing year for treated vs control pools (pure v2 stacks): share of edges with Crossref
     provenance, share whose only provenance is the repository/PDF lane (#1700), share from deduplicated journal articles.
 5a: arXiv-dated split: article had an arXiv copy first posted (arXiv identifier YYMM) in a year before the opening year T,
     vs not (no arXiv copy, or posted in or after T). Applied to treated and control articles alike.
 5b: non-mathematics estimate: stacks whose treated journal's OpenAlex field is not Mathematics.
Out: results/v2/prior_citing.json, results/v2/citing_provenance_by_year.tsv"""
import sys, warnings; warnings.filterwarnings('ignore'); sys.path.insert(0, 'scripts')
from v2_common import *

OUTC = ['cites', 'cites_ja', 'cites_cr', 'cites_ja_cr', 'cites_repo_only']
q = pd.read_csv('data/v2_q10_panel.csv', dtype={'src': 'int64', 'py': 'int64', 'axy': 'int64'})
q['cy'] = q['cy'].astype('Int64')
sz10 = q.groupby(['src', 'py', 'axy'], as_index=False).n_articles.first()
c10 = q.dropna(subset=['cy']).astype({'cy': 'int64'})
st, units = match()
res = []
def runset(d, name, weighted=True, cluster='src'):
    out = [pooled(d, f'{name} | citation-weighted', cluster=cluster)]
    if weighted:
        d = add_weights(d.copy()); out.append(pooled(d[d.we > 0], f'{name} | event-weighted', weights='we', cluster=cluster))
    return out

# 7a
d = build(st, units, cy_df=c10, sz_df=sz10.groupby(['src', 'py'], as_index=False).n_articles.sum(), outcomes=tuple(OUTC))
for o, lab in (('cites', 'all edges, 22 Nov snapshot'), ('cites_ja', 'deduplicated journal articles/reviews citing'),
               ('cites_cr', 'edges with Crossref provenance'), ('cites_ja_cr', 'dedup journal articles/reviews, Crossref provenance')):
    x = d.copy(); x['y'] = x[o]
    for name, xx in (('PURE v2', x[(x.group == 'pure') & (x.platform_move == 0)]), ('ALL v2', x[x.platform_move == 0])):
        for r in runset(xx, f'{name} | {lab}'): res.append(dict(item=7, outcome=o, set=name, **r))
# 7b provenance by citing year (distinct journal-cohort cells per pool)
P = d[(d.group == 'pure') & (d.platform_move == 0)]
cells = P[['src', 'py', 'treated']].drop_duplicates()
pool = c10.merge(cells, on=['src', 'py'])
pool = pool.groupby(['treated', 'cy'])[OUTC].sum().reset_index()
pool = pool[pool.cy >= 1995]
for o in ('cites_ja', 'cites_cr', 'cites_repo_only', 'cites_ja_cr'): pool['share_' + o] = pool[o] / pool.cites
pool['pool'] = np.where(pool.treated == 1, 'treated', 'control')
pool.drop(columns='treated').to_csv(os.path.join(OUT, 'citing_provenance_by_year.tsv'), sep='\t', index=False)
# 5a arXiv split
da = build(st, units, cy_df=c10, sz_df=sz10, split='arxiv')
Pa = da[(da.group == 'pure') & (da.platform_move == 0)]
share = Pa[(Pa.treated == 1) & (Pa.k == Pa.k.min())]  # one row per unit is enough for article counts? use sizes instead below
tre = Pa[Pa.treated == 1].drop_duplicates(['stack', 'src', 'py', 'ax'])
by_prog = tre.groupby(['program', 'ax']).n_articles.sum().unstack(fill_value=0)
by_prog['share_arxiv_before_T'] = by_prog[1] / (by_prog[0] + by_prog[1])
ctl = Pa[Pa.treated == 0].drop_duplicates(['stack', 'src', 'py', 'ax']).groupby('ax').n_articles.sum()
res.append(dict(item=5, note='treated articles by arXiv copy before T (pure v2)', by_program=json.loads(by_prog.to_json(orient='index')),
                control_articles_by_ax={int(k): int(v) for k, v in ctl.items()}))
for axv, lab in ((0, 'no arXiv copy before T'), (1, 'arXiv copy posted before T')):
    for r in runset(Pa[Pa.ax == axv], f'PURE v2 | {lab}'): res.append(dict(item=5, split=lab, set='PURE v2', **r))
    m = Pa[(Pa.ax == axv) & Pa.program.isin(['Elsevier maths open archive 2012', 'AMS back file 2010'])]
    for r in runset(m, f'PURE v2 maths programs | {lab}'): res.append(dict(item=5, split=lab, set='PURE v2, Elsevier maths + AMS', **r))
# interaction-free difference test: pooled with tp x ax
Pa2 = Pa.copy(); Pa2['tp_ax'] = Pa2.tp * Pa2.ax
m = pf.fepois('y ~ tp + tp_ax | unit + s_cy + s_age', data=Pa2, vcov={'CRV1': 'src'})
res.append(dict(item=5, note='difference arXiv-before-T minus none (log points)', b=float(m.coef()['tp_ax']), se=float(m.se()['tp_ax'])))
# 5b non-maths (v1 panel, so directly comparable with v1)
dv = build(st, units)
dv['tfield'] = dv['stack'].map(st.set_index('stack').treated.map(field))
for name, xx in (('PURE v2 non-maths', dv[(dv.group == 'pure') & (dv.platform_move == 0) & (dv.tfield != 'Mathematics')]),
                 ('PURE v2 maths only', dv[(dv.group == 'pure') & (dv.platform_move == 0) & (dv.tfield == 'Mathematics')]),
                 ('ALL v2 non-maths', dv[(dv.platform_move == 0) & (dv.tfield != 'Mathematics')])):
    progs = xx[xx.treated == 1].groupby('program')['stack'].nunique().to_dict()
    for r in runset(xx, name): res.append(dict(item=5, set=name, programs=progs, **r))
    if name == 'PURE v2 non-maths':
        res.append(dict(item=5, set=name, spec='program-date clusters', **clustered_inference(xx, name + ' | pd clusters', cluster='pd', B=4999)))
dump(res, 'prior_citing.json')
