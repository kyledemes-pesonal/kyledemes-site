"""v3 (22 Nov 2026): openings dated 2015-2024 vs 2005-2014 (pure v3, journal clusters, Q12 panel cleaned).
Out: results/v3/more.json"""
import sys, warnings; warnings.filterwarnings('ignore'); sys.path.insert(0, 'scripts')
from v3_common import *
import v3_common as V
V.use_panel(clean=True); st, units = match3(); d = add_weights(build(st, units)); P = pure(d)
res = []
for lab, x in (('PURE v3 openings 2015-2024', P[P['T'] >= 2015]), ('PURE v3 openings 2005-2014', P[P['T'] <= 2014])):
    for wl, w in (('citation-weighted', None), ('event-weighted', 'we'), ('article-weighted', 'wa')):
        xx = x if w is None else x[x[w] > 0]
        res.append(dict(set=lab, weight=wl, **pooled(xx, f'{lab} | {wl}', weights=w)))
dump3(res, 'more.json')
