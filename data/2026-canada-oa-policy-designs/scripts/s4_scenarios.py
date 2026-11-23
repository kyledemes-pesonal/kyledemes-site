"""Step 1 ceiling arithmetic and step 4 scenarios to 2030. All inputs are printed and saved with the outputs."""
import json, csv, os
from oa import RESULTS, MONITOR, load
S1 = load('s1_canada_sets.json')
LAG = load('s1_phasein_lags.json')
PLAT = load('s1_canadian_platforms.json')
# --- phase-in: share of funded papers in publication year Y citing at least one award from 2027 or later,
# using the 2023-2025 distribution of (publication year - newest award year)
cum = {}
for L in range(0, 12):
    vals = []
    for y in ('2023', '2024', '2025'):
        d = {int(k): v for k, v in LAG[y]['lag_newest_award'].items()}; t = sum(d.values())
        vals.append(sum(v for k, v in d.items() if k <= L) / t)
    cum[L] = sum(vals) / len(vals)
phase = {Y: round(cum.get(Y - 2027, 0) if Y >= 2027 else 0, 3) for Y in range(2027, 2036)}
# --- 2025 baseline (OpenAlex, live pull 22 Nov 2026)
ca, tri = S1['canada']['routes']['2025'], S1['tri_ca']['routes']['2025']
nat_open = 100 * (ca['n'] - ca['closed']) / ca['n']
f_oa = tri['n'] / ca['n']
tri_open_oa = 100 * (tri['n'] - tri['closed']) / tri['n']
tri_repo = 100 * S1['tri_ca']['carepo']['2025'] / tri['n']
plat = PLAT['2025']; tri_plat = 100 * plat['canadian_publisher_open'] / plat['tri_ca_total']
# Crossref-only (uniform detection) estimate from the 2024 sample: funded open 73.8% vs all 72.2%
views = {'OpenAlex tags': {'f': f_oa, 'funded_open': tri_open_oa},
         'Uniform detection (Crossref sample)': {'f': 0.30, 'funded_open': 74.0}}
ceiling = []
for v, p in views.items():
    nonf = (nat_open - p['f'] * p['funded_open']) / (1 - p['f'])
    for target in (90, 95):
        full = p['f'] * (target - p['funded_open'])
        ceiling.append({'view': v, 'funded_share_pct': round(100 * p['f'], 1), 'funded_open_2025': round(p['funded_open'], 1),
                        'non_funded_open_2025': round(nonf, 1), 'target_funded_open': target,
                        'national_gain_full_phase_in_pts': round(full, 1),
                        **{f'national_gain_{Y}_pts': round(full * phase[Y], 1) for Y in (2028, 2029, 2030, 2032)}})
# --- ranking among the 55 countries with >= 20,000 papers in 2025 (published oa_by_country.csv)
rows = list(csv.DictReader(open(os.path.join(MONITOR, 'oa_by_country.csv'))))
c25 = {r['code']: 100 * int(r['free_to_read']) / int(r['papers']) for r in rows if r['year'] == '2025' and int(r['papers']) >= 20000 and r['code']}
others = sorted((v for k, v in c25.items() if k != 'CA'), reverse=True)
ca_pub = c25['CA']
def rank(x): return 1 + sum(1 for v in others if v > x)
# --- scenarios to 2030. Others and Canada share a common drift, so the rank moves only with the policy increment.
cov = phase[2030]
SC = {
 'low (no routine checks)': {'covered_funded_open_gain': (0, 2), 'inst_spillover': (0, 0),
     'covered_repo_or_platform': (12, 20), 'uncovered_repo_or_platform': (8, 11),
     'basis': 'Canada 2015 (-6 pts vs peers), NHMRC 2012 (11% in repositories), CIHR fell 60 to 40% compliance, Australia 2012-13 (-1.4 pts vs peers)'},
 'middle (checks through final reports)': {'covered_funded_open_gain': (8, 16), 'inst_spillover': (0, 1),
     'covered_repo_or_platform': (45, 65), 'uncovered_repo_or_platform': (10, 14),
     'basis': 'REF year 1 61% compliant + 20% exceptions; Wellcome 55 to 75%+; FWF 82-92%; H2020 65 to 87%; NHMRC 2022 +10 pts vs peers (mostly hybrid)'},
 'high (checks + institutional rights retention / opt-out deposit)': {'covered_funded_open_gain': (14, 21), 'inst_spillover': (3, 6),
     'covered_repo_or_platform': (80, 92), 'uncovered_repo_or_platform': (20, 35),
     'basis': 'NIH any-repository 54 to 85% within 2 years of the 2008 law (OpenAlex); NIH 83-90% in PMC; UiT >96%; NL green-only +5 pts vs peers 2020-25 under opt-out; UK repository share 14% (COKI)'},
}
out_sc = []
f_lo, f_hi = f_oa, 0.30
for name, s in SC.items():
    # national gain = funded share x coverage x gain in covered funded papers + spillover to everything else
    lo = f_lo * cov * s['covered_funded_open_gain'][0] + s['inst_spillover'][0]
    hi = f_hi * cov * s['covered_funded_open_gain'][1] + s['inst_spillover'][1]
    rlo, rhi = rank(ca_pub + lo), rank(ca_pub + hi)
    # repository/trusted-platform share of tri-agency papers in 2030
    rp_lo = cov * s['covered_repo_or_platform'][0] + (1 - cov) * s['uncovered_repo_or_platform'][0]
    rp_hi = cov * s['covered_repo_or_platform'][1] + (1 - cov) * s['uncovered_repo_or_platform'][1]
    c33 = phase[2033]
    rp33 = (c33 * s['covered_repo_or_platform'][0] + (1 - c33) * s['uncovered_repo_or_platform'][0],
            c33 * s['covered_repo_or_platform'][1] + (1 - c33) * s['uncovered_repo_or_platform'][1])
    out_sc.append({'scenario': name, 'national_gain_2030_pts': [round(lo, 1), round(hi, 1)],
                   'canada_2030_if_common_drift_equals_zero': [round(ca_pub + lo, 1), round(ca_pub + hi, 1)],
                   'rank_2030_of_55': [rlo, rhi], 'tri_repo_or_platform_2030_pct': [round(rp_lo), round(rp_hi)],
                   'tri_repo_or_platform_2033_pct': [round(rp33[0]), round(rp33[1])], **s})
res = {'phase_in_share_of_funded_papers_covered': phase, 'cum_lag_newest_award': {k: round(v, 3) for k, v in cum.items()},
       'baseline_2025': {'national_open': round(nat_open, 1), 'national_open_published_19nov': round(ca_pub, 1),
                         'tri_share_of_canadian_papers_openalex': round(100 * f_oa, 1), 'tri_open_openalex': round(tri_open_oa, 1),
                         'tri_canadian_repository_copy': round(tri_repo, 1), 'tri_open_at_canadian_publisher': round(tri_plat, 1),
                         'rank_of_55': rank(ca_pub)},
       'points_needed_for_rank': {r: round(others[r - 1] - ca_pub + 0.05, 1) for r in (42, 41, 40, 39, 35, 30, 27)},
       'ceiling': ceiling, 'scenarios': out_sc}
json.dump(res, open(os.path.join(RESULTS, 'scenarios.json'), 'w'), indent=1)
print(json.dumps({k: res[k] for k in ('phase_in_share_of_funded_papers_covered', 'baseline_2025', 'points_needed_for_rank')}, indent=0))
for c in ceiling: print(c)
for s in out_sc: print({k: s[k] for k in ('scenario', 'national_gain_2030_pts', 'canada_2030_if_common_drift_equals_zero', 'rank_2030_of_55', 'tri_repo_or_platform_2030_pct', 'tri_repo_or_platform_2033_pct')})
