"""Country-pair article counts, 2000-2025 (type:article), for Canada, each Nordic country (+ Greenland, Faroe Islands)
and comparators, plus the Nordic region as one block (each article counted once). Output ../results/pairs.json
{'pairs': {focal: {year: {partner: count}}}   (the focal country's own key is its total, e.g. pairs.CA.2025.CA)
 'nordic_union': {year: {partner: count, '_total': Nordic articles, '_with_CA': Nordic articles with a Canadian co-author}}}"""
import json, concurrent.futures as cf, oa
FOCAL = ['CA', 'DK', 'FI', 'IS', 'NO', 'SE', 'GL', 'FO', 'US', 'GB', 'DE', 'FR', 'AU', 'NL', 'CH', 'NZ']
from defs import NORDIC
YEARS = range(2000, 2026)
def pull(f, y):
    g = oa.group(f'type:article,publication_year:{y},institutions.country_code:{f}', 'institutions.country_code')
    return f, y, {x['key'].rsplit('/', 1)[-1]: x['count'] for x in g}
out = {'pairs': {}, 'nordic_union': {}}
with cf.ThreadPoolExecutor(6) as ex:
    for f, y, d in ex.map(lambda j: pull(*j), [(f, y) for f in FOCAL for y in YEARS]):
        out['pairs'].setdefault(f, {})[str(y)] = d
    # any-Nordic union: grouped by partner country (each article counted once per partner country)
    for y, d in ex.map(lambda y: (y, {x['key'].rsplit('/', 1)[-1]: x['count'] for x in oa.group(
            f'type:article,publication_year:{y},institutions.country_code:{NORDIC}', 'institutions.country_code')}), YEARS):
        out['nordic_union'][str(y)] = d
    def cnt(y):
        return y, oa.count(f'type:article,publication_year:{y},institutions.country_code:{NORDIC}'), \
            oa.count(f'type:article,publication_year:{y},institutions.country_code:{NORDIC},institutions.country_code:CA')
    for y, tot, ca in ex.map(cnt, YEARS):
        out['nordic_union'][str(y)]['_total'] = tot
        out['nordic_union'][str(y)]['_with_CA'] = ca
json.dump(out, open('../results/pairs.json', 'w'))
print('done')
