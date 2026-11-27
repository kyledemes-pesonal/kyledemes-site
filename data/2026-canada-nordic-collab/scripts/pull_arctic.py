"""Arctic and northern research (title or abstract names an Arctic place, people or feature; list in TERMS),
articles 2000-2025: partner-country counts for Canada's, the Nordic region's, Greenland's and the world's Arctic
papers. Output ../results/arctic.json"""
import json, concurrent.futures as cf, oa
from defs import TERMS, Q
from defs import NORDIC
YEARS = range(2000, 2026)
GROUPS = {'CA': 'institutions.country_code:CA', 'NORDIC': f'institutions.country_code:{NORDIC}',
          'GL': 'institutions.country_code:GL', 'WORLD': None, 'US': 'institutions.country_code:US',
          'RU': 'institutions.country_code:RU', 'WORLD_CORE': 'primary_location.source.is_core:true'}
def pull(g, y):
    f = f'type:article,publication_year:{y},{Q}' + (',' + GROUPS[g] if GROUPS[g] else '')
    d = {x['key'].rsplit('/', 1)[-1]: x['count'] for x in oa.group(f, 'institutions.country_code')}
    d['_total'] = oa.count(f)
    if g == 'CA':
        d['_with_NORDIC'] = oa.count(f + f',institutions.country_code:{NORDIC}')
    if g == 'NORDIC':
        d['_with_CA'] = oa.count(f + ',institutions.country_code:CA')
    return g, y, d
out = {'terms': TERMS, 'by_group': {}}
with cf.ThreadPoolExecutor(3) as ex:
    for g, y, d in ex.map(lambda j: pull(*j), [(g, y) for g in GROUPS for y in YEARS]):
        out['by_group'].setdefault(g, {})[str(y)] = d
json.dump(out, open('../results/arctic.json', 'w'))
print('done')
