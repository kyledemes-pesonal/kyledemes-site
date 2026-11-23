"""Year-by-year projection paths, 2025-2030, for the 2026 tri-agency policy, the February 2025 draft and four designs
used elsewhere. Version 2 (23 Nov 2026), after a pre-publication verification pass.

Changes from version 1:
- One rule for every design's effect: the gain OVER PEERS seen elsewhere (share of the closed gap closed in excess of the
  peer median, or its deposit-only part), applied to Canada's own closed share. Values from results/analogue_tests.csv
  re-run 23 Nov 2026. Version 1 mixed raw before/after changes (which include the general rise that holding everything
  at 2025 removes) with peer-adjusted ones.
- "Home" = an OPEN copy in one of the monitor's Canadian repositories (results/s1b_open_copies.json), not any record.
  From 2026 the lines also count papers free at a Canadian publisher (about 2 in 100 funded papers), which the policy
  accepts as trusted platforms; papers no design reaches otherwise stay at the 2025 level.
- No hidden spill-over on the checked lines (version 1 added up to 1 point, above the post's own ceiling).
- US-style: coverage is every paper accepted from 2027 (half of 2027 papers, all from 2028); compliance builds as NIH's
  did; compliance is in the outcomes, not counted twice.
- UK-style: reach measured (600-paper sample) and effect = deposit part of the UK's excess (with and without paid hybrid).
- Netherlands-style: effect = repository-only excess of Dutch opt-out on OpenAlex (0 to 39% of the closed gap).
- 2025 draft: same checks as line 2, grants from 2026, plus a small preprint bump that is a guess (stated).

Two measures:
  national = share of all Canadian papers (articles + reviews) free to read, OpenAlex, measured today.
  home     = share of tri-agency-funded Canadian papers with an open copy in a Canadian repository (projections also
             count papers free at a Canadian publisher from 2026).
Everything that is not the design is held at its 2025 level. Each scenario gives (lo, hi) per year: lo pairs the
OpenAlex-tag view (26.5% funded, 18% of funded papers closed) with the low effect, hi pairs the level-detection view
(30% funded, 26% closed) with the high effect. The charts plot the midpoint; the 2030 panel shows the range.
Run: python3 scripts/s5_projection_paths.py (no API calls; reads results/scenarios.json and results/s1b_open_copies.json)
"""
import csv, json, os
from oa import RESULTS, MONITOR, load

SC = load('scenarios.json')
OC = load('s1b_open_copies.json')
CSV = os.path.join(MONITOR, 'oa_by_country.csv')

YEARS = list(range(2025, 2031))
SC_P = {int(k): v for k, v in SC['phase_in_share_of_funded_papers_covered'].items()}  # grants awarded from 2027, by pub year
P = {y: SC_P.get(y, 0.0) for y in YEARS}

# --- history
nat_hist = {int(r['year']): round(100 * int(r['free_to_read']) / int(r['papers']), 1)
            for r in csv.DictReader(open(CSV)) if r['code'] == 'CA' and 2010 <= int(r['year']) <= 2025}
home_hist = {int(y): v['pct_open_copy'] for y, v in OC.items() if y.isdigit()}
home_records = {int(y): v['pct_record'] for y, v in OC.items() if y.isdigit()}
B_NAT = nat_hist[2025]                     # 74.3, as published 19 Nov
CLOSED = 100 - B_NAT                       # 25.7: closed share of all Canadian papers, 2025
F = (0.265, 0.30)                          # funded share of Canadian papers (OpenAlex tags; level detection)
FCLOSED = (18.0, 26.0)                     # closed share of funded papers (OpenAlex tags 82% open; Crossref-only 74%)
B_HOME = home_hist[2025]                   # open Canadian repository copy, 2025
PLATFORM = 1.9                             # funded papers free at a Canadian publisher, 2025 (s1_canadian_platforms)
UNCOV = {y: ((B_HOME, B_HOME) if y == 2025 else (B_HOME, B_HOME + PLATFORM)) for y in YEARS}


def lerp(a, b, t):
    return a + (b - a) * t


def ramp(points):
    return {y: points.get(y, 0.0 if y < min(points) else 1.0) for y in YEARS}


def gain(cgap):
    """Points gained on covered funded papers from closing cgap (lo, hi) of their closed gap."""
    return (cgap[0] * FCLOSED[0], cgap[1] * FCLOSED[1])


def funder_line(key, label, cov, g, home_cov, basis, params):
    nat = {y: (B_NAT + F[0] * cov[y] * g[0], B_NAT + F[1] * cov[y] * g[1]) for y in YEARS}
    home = {y: (cov[y] * home_cov[0] + (1 - cov[y]) * UNCOV[y][0], cov[y] * home_cov[1] + (1 - cov[y]) * UNCOV[y][1]) for y in YEARS}
    return dict(key=key, label=label, nat=nat, home=home, basis=basis,
                params=dict(params, gain_on_covered_funded_papers_pts=[round(x, 1) for x in g], home_share_covered=home_cov))


SCEN = []
# 1. 2026 policy, no grant-level checks: Canada 2015, CIHR 2008, NSERC/SSHRC 2015, NHMRC 2012 showed no gain over peers.
SCEN.append(funder_line('as_written_unchecked', '2026 policy, without grant-level checks', P, (0.0, 2.0), (9, 17),
    'Canada 2015, CIHR 2008, NSERC and SSHRC 2015, NHMRC 2012: no gain over peers; NHMRC 11% in repositories; Spain unchecked mandate 14% in repositories',
    dict(coverage='grants awarded from 2027', gain_rule='0 to 2 points (no excess seen)')))
# 2. 2026 policy with grant-level checks: excess share of closed gap closed vs other funders (23 Nov re-run):
#    FWF 17%, H2020 19%, Wellcome 43%.
CHK = (0.17, 0.43)
SCEN.append(funder_line('as_written_checked', '2026 policy, with grant-level checks', P, gain(CHK), (45, 65),
    'Excess share of closed gap closed vs other funders: FWF 17%, H2020 19%, Wellcome 43%; compliance reached: REF year one 61% (+20% exceptions), Wellcome 55% to 75%+',
    dict(coverage='grants awarded from 2027', closed_gap_excess=CHK)))
# 2b. February 2025 draft (science.gc.ca node 1350): grants from 2026, deposit at publication, preprint accepted when
#     the publisher blocks deposit. Same checks as line 2; the preprint bump (+1 to +2 points, +3 to +5 home) is a guess.
PD = {y: (SC_P.get(y + 1, 0.0) if y >= 2026 else 0.0) for y in YEARS}
g2 = gain(CHK)
SCEN.append(funder_line('draft_2025_checked', '2025 draft, with grant-level checks', PD, (g2[0] + 1, g2[1] + 2), (48, 70),
    'As line 2, with grants from 2026 (one year earlier) and a preprint route when publishers block deposit; the preprint bump is a guess',
    dict(coverage='grants awarded from 2026', preprint_bump='+1 to +2 points open, +3 to +5 home (guess)')))
# 3. US-style (NIH 2008): deposit a condition of payment, every paper accepted from 2027.
COV = {2025: 0.0, 2026: 0.0, 2027: 0.5, 2028: 1.0, 2029: 1.0, 2030: 1.0}
ADOPT = {2025: 0.0, 2026: 0.0, 2027: 0.6, 2028: 0.85, 2029: 1.0, 2030: 1.0}
CR = {y: COV[y] * ADOPT[y] for y in YEARS}
NIH = (0.49, 0.49)  # NIH closed 73.5% of its closed gap vs 24.7% for other funders (23 Nov re-run): excess ~49%
SCEN.append(funder_line('us_nih', 'US-style: deposit a condition of payment, every new paper', CR, gain(NIH), (77, 89),
    'NIH 2008: excess ~49% of closed gap vs other funders; repository copies 52% (2007) to 84% (2009); assumes a national service publishers deposit into, as PubMed Central',
    dict(coverage='every paper accepted from 2027', adoption_as_nih=ADOPT, closed_gap_excess=NIH)))
# 4. UK-style (REF): only deposited papers count when you apply. Reaches every paper an applicant lists.
A = ramp({2027: 0.4, 2028: 0.7, 2029: 0.9, 2030: 1.0})
a, c, h = (0.60, 0.80), (0.17, 0.30), (40, 65)
SCEN.append(dict(key='uk_ref', label='UK-style: only deposited papers count when you apply',
    nat={y: (B_NAT + A[y] * a[0] * CLOSED * c[0], B_NAT + A[y] * a[1] * CLOSED * c[1]) for y in YEARS},
    home={y: (lerp(UNCOV[y][0], h[0], A[y]), lerp(UNCOV[y][1], h[1], A[y])) for y in YEARS},
    basis='Reach: 600 random Canadian 2024 papers, 65-72% have a Canadian author with 3-5+ tri-agency-funded papers 2019-25; effect: UK 2013 excess, deposit part ~17% of closed gap, ~30% with paid hybrid',
    params=dict(announcement_ramp=A, applicant_listed_share_of_output=a, closed_gap_closed=c, home_share_2030=h)))
# 5. Netherlands-style: right to share (law assumed 2028) + university opt-out deposit.
U = {2025: (0, 0), 2026: (0, 0), 2027: (0, 0), 2028: (0, 0), 2029: (0.12, 0.25), 2030: (0.25, 0.50)}
c, h = (0.0, 0.39), (75, 95)
SCEN.append(dict(key='nl_taverne', label='Netherlands-style: a right to share, universities deposit',
    nat={y: (B_NAT + U[y][0] * CLOSED * c[0], B_NAT + U[y][1] * CLOSED * c[1]) for y in YEARS},
    home={y: (U[y][0] * h[0] + (1 - U[y][0]) * UNCOV[y][0], U[y][1] * h[1] + (1 - U[y][1]) * UNCOV[y][1]) for y in YEARS},
    basis='Dutch opt-out 2021: repository-only copies +5 vs peers (5 / 12.9 closed = 39%); overall Dutch share did not gain on peers',
    params=dict(university_output_share_running_opt_out=U, closed_gap_closed=c, home_share_at_opt_out_universities=h, law='2028')))
# 6. France-style (HAL): one national archive as the publication record.
R = ramp({2027: 0.25, 2028: 0.5, 2029: 0.75, 2030: 1.0})
n30, h = (1, 4), (35, 60)
SCEN.append(dict(key='fr_hal', label='France-style: one national archive as the publication record',
    nat={y: (B_NAT + R[y] * n30[0], B_NAT + R[y] * n30[1]) for y in YEARS},
    home={y: (lerp(UNCOV[y][0], h[0], R[y]), lerp(UNCOV[y][1], h[1], R[y])) for y in YEARS},
    basis='France PNSO 2018 +2.0 vs peers; ANR-funded 74% free in HAL (2024)', params=dict(ramp=R, national_gain_2030_pts=n30, home_share_2030=h)))

# --- output
r1 = lambda v: round(v, 1)
out = {'version': 2, 'history': {'national': nat_hist, 'home_open_copy': home_hist, 'home_record': home_records},
       'assumptions': {'baseline_held_at_2025': True, 'national_2025': B_NAT, 'closed_2025': round(CLOSED, 1),
                       'funded_share': F, 'funded_closed': FCLOSED, 'home_start_2025_open_copy': B_HOME, 'platform_added_from_2026': PLATFORM,
                       'start': 'each design announced Oct 2026, in force 1 Jan 2027 (NL: law 2028; 2025 draft: grants from 2026)'},
       'scenarios': [{'key': s['key'], 'label': s['label'], 'basis': s['basis'], 'params': s['params'],
                      'national': {y: [r1(s['nat'][y][0]), r1(s['nat'][y][1]), r1(sum(s['nat'][y]) / 2)] for y in YEARS},
                      'home': {y: [r1(s['home'][y][0]), r1(s['home'][y][1]), r1(sum(s['home'][y]) / 2)] for y in YEARS}}
                     for s in SCEN]}
json.dump(out, open(os.path.join(RESULTS, 'projections.json'), 'w'), indent=1, default=list)
with open(os.path.join(RESULTS, 'projections.csv'), 'w', newline='') as fh:
    w = csv.writer(fh)
    w.writerow(['measure', 'series', 'year', 'low', 'high', 'midpoint'])
    for y, v in sorted(nat_hist.items()): w.writerow(['national', 'history', y, v, v, v])
    for y, v in sorted(home_hist.items()): w.writerow(['home', 'history', y, v, v, v])
    for s in out['scenarios']:
        for m in ('national', 'home'):
            for y, (lo, hi, mid) in s[m].items(): w.writerow([m, s['key'], y, lo, hi, mid])
print('national 2025', B_NAT, '| home 2025 open copy', B_HOME)
for s in out['scenarios']:
    print(f"{s['key']:22s} national 2030 {s['national'][2030]}  home 2030 {s['home'][2030]}")
