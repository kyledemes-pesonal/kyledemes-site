"""Rows behind the three charts in the post, built from the saved results (no API calls).
Writes ../results/chart_shares_rows.json (chart 1), chart_arctic_vs_all_rows.json (chart 2) and
chart_priorities_rows.json (chart 3). Shares are out of every 100 Canadian articles."""
import json
R = '../results/'
L = lambda f: json.load(open(R + f))
P, A, PR = L('pairs.json'), L('arctic.json'), L('priorities.json')
ca, nu = P['pairs']['CA'], P['nordic_union']
YEARS = [str(y) for y in range(2000, 2026)]

# Chart 1: share of Canadian articles with a co-author in each partner, 2000-2025
PARTNERS = [('nordic', 'Nordic countries', None), ('gb', 'United Kingdom', 'GB'), ('de', 'Germany', 'DE'),
            ('fr', 'France', 'FR'), ('au', 'Australia', 'AU'), ('nl', 'Netherlands', 'NL')]
rows = []
for y in YEARS:
    for slug, name, cc in PARTNERS:
        n = nu[y]['_with_CA'] if cc is None else ca[y].get(cc, 0)
        rows.append({'year': int(y), 'slug': slug, 'partner': name, 'pct': round(100 * n / ca[y]['CA'], 2), 'n': n})
json.dump(rows, open(R + 'chart_shares_rows.json', 'w'))

# Chart 2: Nordic share of Canada's Arctic and northern articles against all Canadian articles
rows = []
for y in YEARS:
    a = A['by_group']['CA'][y]
    for slug, label, n, t in [('arctic', 'Arctic and northern articles', a['_with_NORDIC'], a['_total']),
                              ('all', 'All articles', nu[y]['_with_CA'], ca[y]['CA'])]:
        rows.append({'year': int(y), 'slug': slug, 'label': label, 'pct': round(100 * n / t, 2), 'n': n, 'tot': t})
json.dump(rows, open(R + 'chart_arctic_vs_all_rows.json', 'w'))

# Chart 3: priority areas, 2021-2025, papers with co-authors in 10 or fewer countries.
# 'tech' = the technology and industry priorities (blue in the chart). 'all' is the reference line; 'health' is not shown.
NAMES = {'spacesci': 'Space science', 'energy': 'Clean energy, incl. nuclear'}
TECH = {'mingeo', 'mining', 'energy', 'ai', 'quantum', 'connectivity', 'spacetech'}
rows = []
for slug, d in PR.items():
    if slug in ('all', 'health'):
        continue
    r = d['2021-2025']
    rows.append({'slug': slug, 'area': NAMES.get(slug, d['name']), 'pct': round(100 * r['CA_NORDIC_le10'] / r['CA_le10'], 1),
                 'joint': r['CA_NORDIC_le10'], 'ca': r['CA_le10'], 'grp': 'tech' if slug in TECH else 'other'})
rows.sort(key=lambda x: -x['pct'])  # stable: ties keep the order of defs.AREAS
a = PR['all']['2021-2025']
json.dump({'rows': rows, 'ref': round(100 * a['CA_NORDIC_le10'] / a['CA_le10'], 1)}, open(R + 'chart_priorities_rows.json', 'w'))
print('done')
