"""v3 (22 Nov 2026) sensitivity: pure v3 without the joiners whose Crossref Elsevier-licence start (not the 2013-07 backfill
date) is a year or more before their Wayback-dated T (HPB 2016-12 vs 2018, Osteoarthritis and Cartilage 2014-02 vs 2018,
J Thoracic Oncology 2015-12 vs 2020, Value in Health Regional Issues 2016-12 vs 2020): those may have opened earlier.
Out: results/v3/joiner_dates.json"""
import sys, warnings; warnings.filterwarnings('ignore'); sys.path.insert(0, 'scripts')
from v3_common import *
import v3_common as V
V.use_panel(clean=True)
jn = {r['source']: r for r in C.rd('data/elsevier_joiners.tsv') if r['source']}
Tj = {e['source']: int(e['T']) for e in V.EV3 if e['program'] == 'Elsevier open archive join'}
early = {s for s, r in jn.items() if s in Tj and r['licence_T'] and r['licence_T'] != '2013-07-01' and int(r['licence_T'][:4]) < Tj[s] - 1}
ev = [e for e in V.EV3 if e['source'] in early and e['v3_status'] == 'pure']
st, units = match3(keep=lambda e: e['source'] not in early)
d = add_weights(build(st, units)); P = pure(d)
res = [dict(dropped=[(e['journal'], e['T'], jn[e['source']]['licence_T']) for e in ev])]
for wl, w in (('citation-weighted', None), ('event-weighted', 'we'), ('article-weighted', 'wa')):
    xx = P if w is None else P[P[w] > 0]
    res.append(dict(weight=wl, **pooled(xx, f'PURE v3 without early-licence joiners | {wl}', weights=w)))
dump3(res, 'joiner_dates.json'); print(res[0], file=sys.stderr)
