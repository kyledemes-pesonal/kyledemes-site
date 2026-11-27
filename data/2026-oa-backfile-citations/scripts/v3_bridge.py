"""v3 (22 Nov 2026): v2 -> v3 bridge, one fix at a time, pure set, citation- and event-weighted, journal clusters, Q12 panel
cleaned (fix 3 in every step). Steps: A v2 pure; B + fix 1 (joiner cohorts start at back_to; the 6 Comptes rendus joiners
fall out because back_to is after the cohort end); C + drop openings that did not hold (BSTJ, Significance, CARJ);
D + move 5 front-list/first-digitization events out of pure (= v3). Out: results/v3/bridge.json"""
import sys, warnings; warnings.filterwarnings('ignore'); sys.path.insert(0, 'scripts')
from v3_common import *
import v3_common as V, v2_common as C
V.use_panel(clean=True)
v1 = C.rd('results/final_events.tsv')
res = []
def run(evs, lab):
    C.events = evs
    st, units = C.match(keep=lambda e: e.get('_st', 'x') != 'dropped')
    st['group'] = st['stack'].map(lambda k: evs[k]['_grp'])
    d = add_weights(build(st, units)); x = d[d.group == 'pure']
    for wl, w in (('citation-weighted', None), ('event-weighted', 'we')):
        xx = x if w is None else x[x[w] > 0]
        res.append(dict(step=lab, weight=wl, **pooled(xx, f'{lab} | {wl}', weights=w, cluster='src')))
def v2grp(e3): return 'pure' if e3['v3_status'] in ('pure', 'front_list') or (e3['v3_status'] == 'dropped' and e3['program'] not in ('single-journal opening (flip)',) and 'platform' not in e3['note'] and not e3['program'].startswith('Annual')) else 'x'
A = [dict(e, _grp=v2grp(e3)) for e, e3 in zip(v1, V.EV3)]
run(A, 'A v2 pure set')
B = [dict(e3, _grp=v2grp(e3)) for e3 in V.EV3]
run(B, 'B + fix 1 joiner cohorts from back_to')
Cc = [dict(e3, _grp=v2grp(e3), _st=('dropped' if e3['v3_status'] == 'dropped' else '')) for e3 in V.EV3]
run(Cc, 'C + drop openings that did not hold')
D = [dict(e3, _grp=('pure' if e3['v3_status'] == 'pure' else 'x'), _st=('dropped' if e3['v3_status'] == 'dropped' else '')) for e3 in V.EV3]
run(D, 'D + front-list moves out (= v3 pure)')
dump3(res, 'bridge.json')
