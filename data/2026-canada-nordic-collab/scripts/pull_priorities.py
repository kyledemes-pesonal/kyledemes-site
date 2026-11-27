"""Canada x Nordic collaboration in the priority areas (defs.AREAS), articles 2016-2020 and 2021-2025.
Output ../results/priorities.json"""
import json, concurrent.futures as cf, oa
from defs import AREAS, NORDIC
def pull(a, yrs):
    slug, name, f = a
    b = f'type:article,publication_year:{yrs}' + (f',{f}' if f else '')
    r = {'world': oa.count(b), 'CA': oa.count(b + ',institutions.country_code:CA'),
         'NORDIC': oa.count(b + f',institutions.country_code:{NORDIC}'),
         'CA_NORDIC': oa.count(b + f',institutions.country_code:CA,institutions.country_code:{NORDIC}'),
         'CA_US': oa.count(b + ',institutions.country_code:CA,institutions.country_code:US'),
         'CA_le10': oa.count(b + ',institutions.country_code:CA,countries_distinct_count:<11'),
         'CA_NORDIC_le10': oa.count(b + f',institutions.country_code:CA,institutions.country_code:{NORDIC},countries_distinct_count:<11'),
         'NORDIC_le10': oa.count(b + f',institutions.country_code:{NORDIC},countries_distinct_count:<11'),
         'world_le10': oa.count(b + ',countries_distinct_count:<11')}
    return slug, yrs, r
out = {}
with cf.ThreadPoolExecutor(3) as ex:
    for slug, yrs, r in ex.map(lambda j: pull(*j), [(a, y) for a in AREAS for y in ['2016-2020', '2021-2025']]):
        out.setdefault(slug, {'name': dict((a[0], a[1]) for a in AREAS)[slug]})[yrs] = r
json.dump(out, open('../results/priorities.json', 'w'))
for slug, d in out.items():
    r, p = d['2021-2025'], d['2016-2020']
    print(f"{d['name'][:34]:34} le10 {100*r['CA_NORDIC_le10']/r['CA_le10']:4.1f} Nside {100*r['CA_NORDIC']/r['NORDIC']:4.1f} CA {r['CA']:6} N {r['NORDIC']:6} joint {r['CA_NORDIC']:5} %CA {100*r['CA_NORDIC']/r['CA']:5.1f} (prev {100*p['CA_NORDIC']/p['CA']:4.1f}) %N {100*r['CA_NORDIC']/r['NORDIC']:4.1f} | le10 {100*r['CA_NORDIC_le10']/r['CA_le10']:4.1f} | CAshareWorld {100*r['CA']/r['world']:4.1f} NshareWorld {100*r['NORDIC']/r['world']:4.1f}")
