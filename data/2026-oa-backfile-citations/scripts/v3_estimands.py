"""v3 (22 Nov 2026): headline estimands on the v3 pure set (and v3 all), one panel (Q12, cleaned).
Three weightings (citation-, article-, event-weighted), program-date clusters: CRV1 t(G-1), score wild-cluster bootstrap
(9,999 draws) p and test-inversion CI, MDE at 80% power; journal-clustered CI alongside. Plus a step-by-step bridge from v2
(pure, citation- and event-weighted, journal clusters): v2 events on the Q12 panel uncleaned (snapshot), + fix 3 (records),
+ fixes 1, 2, 4 (= v3). Pure without Cell Press and leave-one-program-out. Out: results/v3/estimands.json"""
import sys, warnings; warnings.filterwarnings('ignore'); sys.path.insert(0, 'scripts')
from v3_common import *
import v3_common as V, v2_common as C
res = []
W = {'citation-weighted': None, 'event-weighted': 'we', 'article-weighted': 'wa'}
def two(x, lab, item):
    for wl, w in (('citation-weighted', None), ('event-weighted', 'we')):
        xx = x if w is None else x[x[w] > 0]
        res.append(dict(item=item, set=lab, weight=wl, **pooled(xx, f'{lab} | {wl}', weights=w, cluster='src')))
# bridge
V.use_panel(clean=False); V.use_events(False)
st, units = C.match(); d = add_weights(build(st, units))
two(d[(d.group == 'pure') & (d.platform_move == 0)], 'bridge 1: v2 pure, Q12 panel uncleaned', 'bridge')
V.use_panel(clean=True); V.use_events(False)
st, units = C.match(); d = add_weights(build(st, units))
two(d[(d.group == 'pure') & (d.platform_move == 0)], 'bridge 2: v2 pure, Q12 panel cleaned (fix 3)', 'bridge')
st, units = match3(); st.to_csv(os.path.join(OUT3, 'stacks_v3.tsv'), sep='\t', index=False)
d = add_weights(build(st, units))
P = pure(d); A = d[d.platform_move == 0]
for name, x in (('PURE v3', P), ('ALL v3', A)):
    for wl, w in W.items():
        xx = x if w is None else x[x[w] > 0]
        r = clustered_inference(xx, f'{name} | {wl}', weights=w, cluster='pd', B=9999)
        r2 = pooled(xx, f'{name} | {wl} (journal clusters)', weights=w, cluster='src', quiet=True)
        r.update(src_lo95=r2['lo95'], src_hi95=r2['hi95'])
        res.append(dict(item='main', set=name, weight=wl, **r))
        dump3(res, 'estimands.json')
x = P[P.program != 'Cell Press archive 2005']
for wl, w in W.items():
    xx = x if w is None else x[x[w] > 0]
    res.append(dict(item='no Cell Press', set='PURE v3 without Cell Press', weight=wl, **clustered_inference(xx, f'PURE v3 no Cell Press | {wl}', weights=w, cluster='pd', B=4999)))
for prog in sorted(P.program.unique()):
    x = P[P.program != prog]
    for wl, w in (('citation-weighted', None), ('event-weighted', 'we')):
        xx = x if w is None else x[x[w] > 0]
        res.append(dict(item='leave one out', set=f'PURE v3 leave out: {prog}', weight=wl, **pooled(xx, f'PURE v3 leave out {prog[:30]} | {wl}', weights=w, cluster='pd')))
ps = st[st.group == 'pure']
res.append(dict(item='clusters', G=int(ps.pd.nunique()), stacks_per_cluster=ps.groupby('pd').size().to_dict(),
                treated_articles_per_cluster=ps.groupby('pd').treated_n.sum().to_dict()))
dump3(res, 'estimands.json')
