"""Every OpenAlex number in the post, recomputed from the saved results (no API calls).
Writes ../results/post_numbers.json and prints it. MANIFEST.md says which key backs which sentence.
Shares are percentages; 'x' values are ratios (2025 share / 2000 share)."""
import json
R = '../results/'
L = lambda f: json.load(open(R + f))
P, A, PR, S = L('pairs.json'), L('arctic.json'), L('priorities.json'), L('subfields.json')
C, I, O, CP = L('context.json'), L('institutions.json'), L('open.json'), L('check_programmes.json')
pct = lambda a, b: round(100 * a / b, 2)
ca, nu = P['pairs']['CA'], P['nordic_union']
out = {}

# How much do they already work together? (pairs.json, context.json, subfields.json)
share = lambda y, cc: pct(nu[y]['_with_CA'] if cc == 'NORDIC' else ca[y].get(cc, 0), ca[y]['CA'])
partners_2025 = {cc: share('2025', cc) for cc in [k for k in ca['2025'] if k != 'CA'] + ['NORDIC']}
ranked = sorted(partners_2025, key=lambda k: -partners_2025[k])
out['canada_side'] = {
    'canadian_articles_2025': ca['2025']['CA'], 'with_nordic_2025': nu['2025']['_with_CA'],
    'nordic_share_2000': share('2000', 'NORDIC'), 'nordic_share_2025': share('2025', 'NORDIC'),
    'nordic_x_since_2000': round(share('2025', 'NORDIC') / share('2000', 'NORDIC'), 2),
    'partners_2025_top10': [[k, partners_2025[k]] for k in ranked[:10]],
    'nordic_rank_2025': ranked.index('NORDIC') + 1,
    'nordic_countries_2025': {cc: share('2025', cc) for cc in ['SE', 'DK', 'NO', 'FI', 'IS', 'GL', 'FO']},
    'x_since_2000': {cc: round(share('2025', cc) / share('2000', cc), 2) for cc in ['NORDIC', 'GB', 'DE', 'FR', 'AU', 'NL']},
    'international_share': {y: pct(*C['intl'][y]) for y in ('2000', '2025')},
}
nordic_side = {}
for y in ('2000', '2025'):
    n = nu[y]
    d = {k: pct(v, n['_total']) for k, v in n.items() if not k.startswith('_') and k not in 'DK FI IS NO SE GL FO AX'.split()}
    rk = sorted(d, key=lambda k: -d[k])
    nordic_side[y] = {'nordic_articles': n['_total'], 'with_canada': n['_with_CA'], 'canada_share': pct(n['_with_CA'], n['_total']),
                      'canada_rank': rk.index('CA') + 1, 'top12': [[k, round(d[k], 1)] for k in rk[:12]]}
out['nordic_side'] = nordic_side
g = C['greenland_2021_2025']
out['greenland_2021_2025'] = {'articles': g['_total'], 'with_canada': g['CA'], 'canada_share': pct(g['CA'], g['_total']),
                              'top_partners': sorted([[k, v] for k, v in g.items() if k not in ('_total', 'GL')], key=lambda x: -x[1])[:4]}
le = C['le10']
out['consortia'] = {
    'joint_2021_2025_all': S['CA_NORDIC']['total'], 'joint_2021_2025_le10': S['CA_NORDIC_le10']['total'],
    'share_with_11plus_countries': round(100 - pct(S['CA_NORDIC_le10']['total'], S['CA_NORDIC']['total']), 1),
    'le10_x_since_2000': {c: round(pct(le['2025'][c], le['2025']['_total']) / pct(le['2000'][c], le['2000']['_total']), 2)
                          for c in ['NORDIC', 'GB', 'DE']},
    'le10_share': {c: [pct(le['2000'][c], le['2000']['_total']), pct(le['2025'][c], le['2025']['_total'])] for c in ['NORDIC', 'GB', 'DE']},
}

# What do they work on together? (arctic.json, subfields.json, institutions.json)
a = A['by_group']['CA']
out['arctic_canada'] = {y: {'articles': a[y]['_total'], 'with_nordic': a[y]['_with_NORDIC'], 'nordic_share': pct(a[y]['_with_NORDIC'], a[y]['_total']),
                            **{cc + '_share': pct(a[y].get(cc, 0), a[y]['_total']) for cc in ['US', 'GB', 'DE', 'FR']}}
                        for y in ['2000'] + [str(y) for y in range(2016, 2026)]}
out['arctic_vs_all_2025_ratio'] = round(pct(a['2025']['_with_NORDIC'], a['2025']['_total']) / share('2025', 'NORDIC'), 2)
nA = A['by_group']['NORDIC']
out['arctic_nordic_side'] = {y: {'articles': nA[y]['_total'], **{cc + '_share': pct(nA[y].get(cc, 0), nA[y]['_total']) for cc in ['RU', 'CA', 'DE', 'CN']}}
                             for y in ('2021', '2025')}
w = A['by_group']['WORLD']
out['nordic_share_of_world_arctic'] = {f'{p0}-{p1}': pct(sum(nA[str(y)]['_total'] for y in range(p0, p1 + 1)),
                                                        sum(w[str(y)]['_total'] for y in range(p0, p1 + 1)))
                                       for p0, p1 in [(2021, 2025), (2016, 2025)]}
f1, f0 = S['CA_NORDIC_le10']['field'], S['CA_le10']['field']
out['fields_le10'] = sorted([[v[0], pct(f1.get(k, ['', 0])[1], v[1]), f1.get(k, ['', 0])[1], v[1]] for k, v in f0.items()], key=lambda x: -x[1])
f1, f0 = S['CA_NORDIC']['field'], S['CA']['field']
out['fields_all_papers'] = sorted([[v[0], pct(f1.get(k, ['', 0])[1], v[1]), f1.get(k, ['', 0])[1], v[1]] for k, v in f0.items()], key=lambda x: -x[1])
out['institutions_top3'] = {grp: {c: [[i[1], i[2]] for i in I[grp]['by_country'][c]['institutions'][:4]] for c in ['CA', 'DK', 'SE', 'NO', 'GL']}
                            for grp in ('all', 'arctic')}

# Where is the room to grow? (priorities.json, check_programmes.json, institutions.json)
pr = {}
for slug, d in PR.items():
    r, p = d['2021-2025'], d['2016-2020']
    pr[slug] = {'name': d['name'], 'canada_side_le10': round(100 * r['CA_NORDIC_le10'] / r['CA_le10'], 1),
                'nordic_side_le10': round(100 * r['CA_NORDIC_le10'] / r['NORDIC_le10'], 1),
                'joint_le10': r['CA_NORDIC_le10'], 'joint_all_2016_2020': p['CA_NORDIC'], 'joint_all_2021_2025': r['CA_NORDIC'],
                'canada_growth': round(r['CA'] / p['CA'], 2), 'canada_share_of_world': round(100 * r['CA'] / r['world'], 1),
                'nordic_side_all': round(100 * r['CA_NORDIC'] / r['NORDIC'], 1),
                'x_overall_rate': round((r['CA_NORDIC_le10'] / r['CA_le10']) / (PR['all']['2021-2025']['CA_NORDIC_le10'] / PR['all']['2021-2025']['CA_le10']), 2)}
out['priority_areas_2021_2025'] = pr
out['nordforsk_on_joint_2016_2025'] = CP['nordforsk_on_joint']
out['funders_on_joint_2021_2025_le10_top6'] = [[f[1], f[2]] for f in I['all']['funders_le10'][:6]]

# Open research infrastructure (open.json)
out['free_to_read_2024'] = {c: {'articles': r['total'], 'free_to_read': pct(r['total'] - r['oa_status'].get('closed', 0), r['total']),
                                'at_publisher': pct(sum(r['oa_status'].get(k, 0) for k in ('gold', 'hybrid', 'diamond', 'bronze')), r['total']),
                                'green_only': pct(r['oa_status'].get('green', 0), r['total'])}
                            for c, r in O.items() if c in ('CA', 'DK', 'FI', 'IS', 'NO', 'SE')}

json.dump(out, open(R + 'post_numbers.json', 'w'), indent=1, ensure_ascii=False)
print(json.dumps(out, indent=1, ensure_ascii=False)[:6000])
