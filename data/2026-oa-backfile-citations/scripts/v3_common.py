"""v3 shared code (22 Nov 2026). Reuses v2_common's matching, panel build, PPML and bootstrap (imported, not copied), with:
 - events from results/v3/final_events_v3.tsv (v3 cohort bounds and status; see v3_events.py);
 - ONE panel for every v3 estimate: data/v3_q12_panel.csv (Q12, pulled 22 Nov 2026 ~18:28 UTC), cleaned for fix 3:
   per source, 'home' DOI prefixes = non-JSTOR prefixes holding >= 10% of the source's DOI'd non-JSTOR records 1880-2023.
   In each (source, publication year) cell that has home-prefix records: (a) JSTOR 10.2307 records are dropped (duplicates of
   the publisher's records; many are book reviews carrying the reviewed book's citations); (b) records with no DOI or a
   foreign prefix are dropped when they are > 20% of the cell (misassigned records, e.g. Information and Computation).
   Cells with no home-prefix record keep everything (the JSTOR or no-DOI record is the only copy). Same rule for treated and
   control journals.
 - groups: pure = v3_status 'pure'; 'front_list' events join the other-flips group; 'dropped' events are removed.
Outcomes in the panel: cites (all served edges), cites_ja (journal articles/reviews citing, each counted once), cites_repo_only
(edges whose only provenance is the repository/PDF lane), cites_ja_cr (journal articles citing once, edge filed on the DOI
record: provenance label 'crossref', which since Nov 2026 also covers PDF and landing-page lists filed on DOI records)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v2_common as C
from v2_common import *  # noqa: F401,F403 (pooled, clustered_inference, event_study, add_weights, pct, ...)
import numpy as np, pandas as pd

OUT3 = os.path.join(C.ROOT, 'results', 'v3'); os.makedirs(OUT3, exist_ok=True)
C.OUT = OUT3
OUTCOMES = ['cites', 'cites_ja', 'cites_repo_only', 'cites_ja_cr']

raw = pd.read_csv('data/v3_q12_panel.csv', dtype={'src': 'int64', 'py': 'int64', 'pfx': 'str'}, keep_default_na=False, na_values={'cy': ['']})
raw['cy'] = pd.to_numeric(raw['cy'], errors='coerce').astype('Int64')
recs = raw.groupby(['src', 'py', 'pfx'], as_index=False).n_articles.first()
tot = recs[(recs.pfx != 'none') & (recs.pfx != '10.2307')].groupby(['src', 'pfx']).n_articles.sum()
share = tot / tot.groupby(level='src').transform('sum')
HOME = share[share >= 0.10].reset_index().groupby('src').pfx.apply(set).to_dict()
recs['cls'] = [('home' if p in HOME.get(s, ()) else 'jstor' if p == '10.2307' else 'other') for s, p in zip(recs.src, recs.pfx)]
cell = recs.pivot_table(index=['src', 'py'], columns='cls', values='n_articles', aggfunc='sum', fill_value=0)
for c in ('home', 'jstor', 'other'):
    if c not in cell: cell[c] = 0
cell['n'] = cell[['home', 'jstor', 'other']].sum(1)
cell['drop_jstor'] = cell.home > 0
cell['drop_other'] = (cell.home > 0) & (cell.other > 0.2 * cell.n)
recs = recs.merge(cell[['drop_jstor', 'drop_other']].reset_index(), on=['src', 'py'])
recs['keep'] = ~(((recs.cls == 'jstor') & recs.drop_jstor) | ((recs.cls == 'other') & recs.drop_other))
KEEPRECS = recs

def make_panel(clean=True):
    r = raw.merge(recs[['src', 'py', 'pfx', 'keep']], on=['src', 'py', 'pfx'])
    if clean: r = r[r.keep]
    sz = r.groupby(['src', 'py', 'pfx'], as_index=False).n_articles.first().groupby(['src', 'py'], as_index=False).n_articles.sum()
    ct = r.dropna(subset=['cy']).astype({'cy': 'int64'}).groupby(['src', 'py', 'cy'], as_index=False)[OUTCOMES].sum()
    return ct, sz

def use_panel(clean=True):
    """Point v2_common's globals (used by match/build) at the Q12 panel."""
    ct, sz = make_panel(clean)
    C.cit, C.sizes = ct, sz
    C.jc = ct.groupby(['src', 'py', 'cy'])['cites'].sum()
    C.jn = sz.groupby(['src', 'py'])['n_articles'].sum()
    return ct, sz

EV3 = C.rd('results/v3/final_events_v3.tsv')
def use_events(v3=True):
    C.events = EV3 if v3 else C.rd('results/final_events.tsv')

GROUP3 = {'pure': 'pure', 'annual_reviews': 'Annual Reviews S2O', 'other_flip': 'other flips', 'front_list': 'other flips', 'platform_move': 'other flips'}
def match3(mode='v1', keep=None, cand_filter=None):
    """v3 events (dropped removed), v3 groups. Stack ids index EV3 (same order as v1 final_events.tsv)."""
    use_events(True)
    k0 = (lambda e: e['v3_status'] != 'dropped' and (keep is None or keep(e)))
    st, units = C.match(mode=mode, keep=k0, cand_filter=cand_filter)
    stat = {k: EV3[k]['v3_status'] for k in st['stack']}
    st['v3_status'] = st['stack'].map(stat)
    st['group'] = st['v3_status'].map(GROUP3)
    st['platform_move'] = (st['v3_status'] == 'platform_move').astype(int)
    return st, units

def pure(d): return d[d.group == 'pure']
def dump3(obj, name): json.dump(obj, open(os.path.join(OUT3, name), 'w'), indent=1, default=float)
