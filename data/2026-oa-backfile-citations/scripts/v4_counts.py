"""v4 (27 Nov 2026), step 1: how many opened papers were 1 to 2 years old at opening?
Read-only on v1-v3. Uses the v3 events, v3 matching (match3) and the one v3 panel (Q12, cleaned as in v3); writes only to
results/v4_recent/. Age at opening = T - publication year (year resolution, as in v3's age split): age 1 = published the
calendar year before the opening year, age 2 = two years before. v3 cohorts are "publication years fully opened on T".
Also counts the v4 extension cohort: the T-1 year of pure openings in 12-month-wall programs (Cell Press 2005; Elsevier
open-archive joiners whose Wayback list says "embargo 12 months"), which v3 leaves out because those papers opened month
by month during year T (the dropped donut year), not all on T.
Run: .venv/bin/python -I scripts/v4_counts.py  (workspace venv: pandas/pyfixest, as v3)
Out: results/v4_recent/counts_by_event.tsv, counts.json"""
import sys, os, json, warnings
warnings.filterwarnings('ignore')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # published copy: the folder above scripts/
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from v3_common import *  # noqa
import v3_common as V, v2_common as C
OUT4 = os.path.join(ROOT, 'results', 'v4_recent')
C.OUT = OUT4; V.OUT3 = OUT4  # any accidental dump()/dump3() lands in v4, never in v2/v3

ct, sz = V.use_panel(clean=True)
st, units = match3()
SZ = sz.groupby(['src', 'py']).n_articles.sum()
def n(s, a, b):
    return int(sum(int(SZ.get((s, y), 0)) for y in range(a, b + 1)))
def wall12(r):
    return (r.program == 'Cell Press archive 2005') or (r.program == 'Elsevier open archive join' and 'embargo 12 months' in str(r.note))

rows = []
for _, r in st.iterrows():
    s, T, lo, hi = int(r.treated), int(r['T']), int(r.lo), int(r.hi)
    rows.append(dict(stack=int(r['stack']), journal=r.journal, program=r.program, group=r.group, v3_status=r.v3_status, pd=r.pd,
                     T=T, cohort_from=lo, cohort_to=hi, youngest_age=T - hi,
                     papers_opened=n(s, lo, hi),
                     age1=n(s, max(lo, T - 1), min(hi, T - 1)) if hi >= T - 1 else 0,
                     age2=n(s, max(lo, T - 2), min(hi, T - 2)) if hi >= T - 2 and lo <= T - 2 else 0,
                     age3_5=n(s, max(lo, T - 5), min(hi, T - 3)) if hi >= T - 5 else 0,
                     ext_age1_wall12=(n(s, T - 1, T - 1) if (r.group == 'pure' and wall12(r) and hi == T - 2) else 0),
                     n_controls=len(str(r.controls).split()), n_date_sources=int(r.n_date_sources)))
ev = pd.DataFrame(rows)
ev['age1_2'] = ev.age1 + ev.age2
ev['ar'] = np.where(ev.program.str.startswith('Annual Reviews S2O 2023'), 'Annual Reviews S2O 2023',
                    np.where(ev.program.str.startswith('Annual Reviews S2O pilot'), 'Annual Reviews S2O pilots', ''))
ev['set'] = np.select([ev.group == 'pure', ev.ar != '', ev.v3_status == 'platform_move'],
                      ['pure', ev.ar, 'other flips (platform move at T)'], 'other flips / front list (no platform move)')
ev.sort_values(['set', 'program', 'T', 'journal']).to_csv(os.path.join(OUT4, 'counts_by_event.tsv'), sep='\t', index=False)

def summ(x):
    y = x[x.age1_2 > 0]
    return dict(events=int(len(x)), papers_opened=int(x.papers_opened.sum()),
                events_with_age1_2=int(len(y)), papers_age1=int(x.age1.sum()), papers_age2=int(x.age2.sum()),
                papers_age1_2=int(x.age1_2.sum()), share_of_opened=float(x.age1_2.sum() / max(1, x.papers_opened.sum())),
                program_date_clusters_age1_2=int(y.pd.nunique()),
                by_program={p: dict(events=int(len(g)), papers_age1=int(g.age1.sum()), papers_age2=int(g.age2.sum()))
                            for p, g in y.groupby('program')},
                ext_age1_wall12_events=int((x.ext_age1_wall12 > 0).sum()), ext_age1_wall12_papers=int(x.ext_age1_wall12.sum()))
out = {s: summ(g) for s, g in ev.groupby('set')}
out['all flips and S2O'] = summ(ev[ev.set != 'pure'])
out['note'] = ('v3 stacks (176 matched openings; 4 non-dropped v3 events without 2 matched controls hold no 1-2 year-old papers). '
               'Papers = articles+reviews in the cleaned Q12 panel (v3 fix 3). Age = T - publication year.')
json.dump(out, open(os.path.join(OUT4, 'counts.json'), 'w'), indent=1)
for k, v in out.items():
    if isinstance(v, dict):
        print(f"{k:45s} events {v['events']:3d} opened {v['papers_opened']:7d} | with age1-2: {v['events_with_age1_2']:3d} events, "
              f"age1 {v['papers_age1']:6d}, age2 {v['papers_age2']:6d} ({100*v['share_of_opened']:.1f}%), G {v['program_date_clusters_age1_2']}"
              f" | ext age1 (12-month wall): {v['ext_age1_wall12_events']} events, {v['ext_age1_wall12_papers']} papers")
