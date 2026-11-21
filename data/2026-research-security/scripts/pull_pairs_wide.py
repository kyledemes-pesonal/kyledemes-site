"""Wider donor pool for the event study (review concern 2): country-pair counts (spec 'all': type:article) for 16
more focal countries, 2010-2025. Output ../results/pairs_wide.json {focal: {year: {partner: count}}}"""
import json, concurrent.futures as cf, oa
EXTRA = ['IT', 'ES', 'CH', 'SE', 'KR', 'SG', 'NZ', 'BE', 'AT', 'DK', 'NO', 'FI', 'IE', 'IL', 'PT', 'PL']
def pull(f, y):
    g = oa.group(f'type:article,publication_year:{y},institutions.country_code:{f}', 'institutions.country_code')
    return f, y, {x['key'].rsplit('/', 1)[-1]: x['count'] for x in g}
out = {}
with cf.ThreadPoolExecutor(4) as ex:
    for f, y, d in ex.map(lambda j: pull(*j), [(f, y) for f in EXTRA for y in range(2010, 2026)]):
        out.setdefault(f, {})[str(y)] = d
old = json.load(open('../results/pairs.json'))['all']
for f in ['CA', 'US', 'GB', 'AU', 'DE', 'FR', 'JP', 'NL']: out[f] = old[f]
json.dump(out, open('../results/pairs_wide.json', 'w'))
print('done', len(out))
