"""Step 2 tests: change from the year before an instrument to 3, 4 and 5 years after, against the median change
of peers over the same years. Countries: peers = the other 15 high-income countries. Funders: peers = the
other funders in the panel with >= 300 papers in both years (excluding the treated group), and the gap to
the funder's own country."""
import json, statistics as st
from oa import *
D = load('s2_analogue_sets.json')
HI = [k for k in D if k.startswith('country:')]
FUNDERS = [k for k in D if k.startswith('funder:')]
def m(name, y, metric):
    s = D[name]; r = s['routes'].get(str(y))
    if not r or r['n'] < 300: return None
    n = r['n']
    if metric == 'open': return 100 * (n - r.get('closed', 0)) / n
    if metric == 'green_only': return 100 * r.get('green', 0) / n
    if metric == 'any_repo': return 100 * s['anyrepo'].get(str(y), 0) / n
    if metric == 'hybrid': return 100 * r.get('hybrid', 0) / n
    if metric == 'gold_diamond': return 100 * (r.get('gold', 0) + r.get('diamond', 0)) / n
def chg(name, y0, y1, metric):
    a, b = m(name, y0, metric), m(name, y1, metric)
    return None if a is None or b is None else b - a
def test(treated, year, peers, metrics=('open', 'any_repo', 'green_only', 'hybrid', 'gold_diamond'), country=None, label=''):
    pre = year - 1
    row = {'label': label, 'treated': treated, 'event_year': year, 'pre_year': pre}
    for k in (3, 4, 5):
        post = year + k
        if post > 2025: continue
        for met in metrics:
            c = chg(treated, pre, post, met)
            pc = [chg(p, pre, post, met) for p in peers if p not in (treated if isinstance(treated, list) else [treated])]
            pc = [x for x in pc if x is not None]
            if c is None: continue
            row[f'{met}_t+{k}'] = round(c, 1)
            row[f'{met}_t+{k}_peer_median'] = round(st.median(pc), 1) if pc else None
            row[f'{met}_t+{k}_excess'] = round(c - st.median(pc), 1) if pc else None
            if country:
                cc = chg(country, pre, post, met)
                row[f'{met}_t+{k}_vs_country'] = round(c - cc, 1) if cc is not None else None
    # headroom yardstick: share of the pre-year closed papers' share that was opened by t+k, vs peers
    for k in (3, 4, 5):
        post = year + k
        if post > 2025: continue
        def gap(n):
            a, b = m(n, pre, 'open'), m(n, post, 'open')
            return None if a is None or b is None or a >= 100 else 100 * (b - a) / (100 - a)
        g = gap(treated); pg = [gap(p) for p in peers if p != treated]; pg = [x for x in pg if x is not None]
        if g is not None:
            row[f'closed_gap_cut_t+{k}'] = round(g, 1)
            row[f'closed_gap_cut_t+{k}_peer_median'] = round(st.median(pg), 1) if pg else None
            row[f'closed_gap_cut_t+{k}_excess'] = round(g - st.median(pg), 1) if pg else None
    for met in ('open', 'any_repo'):
        row[f'{met}_level_pre'] = round(m(treated, pre, met), 1) if m(treated, pre, met) is not None else None
    return row
NAT = [('country:US', 2008, 'NIH 2008 law (US national)'), ('country:US', 2013, 'Holdren memo / NIH holds (US national)'),
       ('country:GB', 2013, 'RCUK policy + Finch (UK national)'), ('country:GB', 2016, 'REF deposit rule (UK national)'),
       ('country:NL', 2015, 'Taverne right in law + national deals (NL national)'), ('country:NL', 2019, 'Taverne pilot, then opt-out 2021-24 (NL national)'),
       ('country:NL', 2021, 'Institutional opt-out Taverne roll-out 2021-24 (NL national)'), ('country:GB', 2021, 'UKRI immediate OA 2022 + REF (UK national)'), ('country:DE', 2019, 'DEAL Wiley 2019 / Springer Nature 2020 (DE national)'), ('country:SE', 2017, 'Bibsam TAs (SE national)'),
       ('country:NO', 2017, 'National goal + deposit norm, Unit deals (NO national)'), ('country:FI', 2017, 'FinELib TAs (FI national)'),
       ('country:AU', 2013, 'NHMRC 2012 / ARC 2013 12-month deposit (AU national)'), ('country:FR', 2018, 'PNSO 1, HAL, BSO (FR national)'),
       ('country:CH', 2017, 'National strategy (CH national)'), ('country:AT', 2014, 'FWF/IOP first TA (AT national)'),
       ('country:CA', 2015, 'Tri-agency harmonized policy (CA national)'), ('country:CA', 2008, 'CIHR policy (CA national)'),
       ('country:JP', 2017, 'JST/JSPS in-principle OA (JP national)')]
FUN = [('funder:NIH', 2008, 'NIH 2008 law', 'country:US'), ('funder:NIH', 2013, 'NIH continuation-award holds', 'country:US'),
       ('funder:Wellcome', 2012, 'Wellcome sanctions', 'country:GB'), ('funder:UKRI+councils', 2013, 'RCUK policy + APC block grants', 'country:GB'),
       ('funder:UKRI+councils', 2016, 'REF deposit rule (UKRI-funded)', 'country:GB'), ('funder:CIHR', 2008, 'CIHR 2008 policy', 'country:CA'),
       ('funder:NSERC', 2015, 'Tri-agency 2015 (NSERC)', 'country:CA'), ('funder:SSHRC', 2015, 'Tri-agency 2015 (SSHRC)', 'country:CA'),
       ('funder:CIHR', 2015, 'Tri-agency 2015 (CIHR, deposit-on-publication dropped)', 'country:CA'),
       ('funder:NHMRC', 2012, 'NHMRC 12-month deposit, unchecked', 'country:AU'), ('funder:ARC', 2013, 'ARC 12-month deposit', 'country:AU'),
       ('funder:FWF', 2014, 'FWF + first TA', 'country:AT'), ('funder:European Commission', 2014, 'H2020 mandate', None),
       ('funder:NSF', 2016, 'NSF public access (end of voluntary)', 'country:US'), ('funder:NHMRC', 2022, 'NHMRC immediate OA (2022/2024)', 'country:AU')]
PLANS_MEMBERS = ['funder:NWO', 'funder:UKRI+councils', 'funder:FWF', 'funder:ANR', 'funder:RCN Norway', 'funder:Wellcome', 'funder:Gates', 'funder:Formas']
PLANS_CONTROLS = ['funder:NIH', 'funder:NSF', 'funder:DFG', 'funder:JSPS', 'funder:Tri-agency', 'funder:NHMRC', 'funder:ARC', 'funder:VR Sweden']
rows = []
for t, y, lab in NAT:
    rows.append({'kind': 'national', **test(t, y, HI, label=lab)})
for t, y, lab, c in FUN:
    rows.append({'kind': 'funder', **test(t, y, FUNDERS, country=c, label=lab)})
# Plan S: each member vs median of controls
for t in PLANS_MEMBERS:
    rows.append({'kind': 'planS_member', **test(t, 2021, PLANS_CONTROLS, label='Plan S 2021 (member vs non-member funders)')})
for t in PLANS_CONTROLS:
    rows.append({'kind': 'planS_control', **test(t, 2021, [x for x in PLANS_CONTROLS if x != t], label='Plan S 2021 control')})
# UiT rights retention (~2021/22; date not verified) vs rest of Norway
for y in (2021, 2022):
    rows.append({'kind': 'institution', **test('inst:UiT', y, ['inst:NO_not_UiT'], label=f'UiT rights retention (event year {y}, date unverified) vs rest of Norway')})
json.dump(rows, open(os.path.join(RESULTS, 'analogue_tests.json'), 'w'), indent=1)
import csv
keys = sorted({k for r in rows for k in r}, key=lambda k: (k not in ('kind','label','treated','event_year','pre_year'), k))
with open(os.path.join(RESULTS, 'analogue_tests.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(rows)
for r in rows:
    k = 4 if f'open_t+4' in r else 3
    print(f"{r['label'][:58]:58s} {r['treated'][-12:]:12s} pre={r.get('open_level_pre')} open {r.get(f'open_t+{k}')} peer {r.get(f'open_t+{k}_peer_median')} ex {r.get(f'open_t+{k}_excess')} | repo {r.get(f'any_repo_t+{k}')} ex {r.get(f'any_repo_t+{k}_excess')} | green ex {r.get(f'green_only_t+{k}_excess')} | hyb ex {r.get(f'hybrid_t+{k}_excess')} | vsC {r.get(f'open_t+{k}_vs_country')} | gapcut {r.get(f'closed_gap_cut_t+{k}')} peer {r.get(f'closed_gap_cut_t+{k}_peer_median')} ex {r.get(f'closed_gap_cut_t+{k}_excess')} (t+{k})")
