"""Programme footprints in OpenAlex: NordForsk as a credited funder on Canada x Nordic articles; Arctic Science
Partnership institutions (Aarhus University, Greenland Institute of Natural Resources, University of Manitoba)
co-authoring, by year. Output ../results/check_programmes.json"""
import json, oa
from defs import NORDIC, Q
out = {}
r = oa.get('/funders', search='NordForsk', per_page=5)
out['nordforsk_ids'] = [(f['id'], f['display_name'], f['works_count']) for f in r['results']]
B = f'type:article,publication_year:2016-2025,institutions.country_code:CA,institutions.country_code:{NORDIC}'
out['nordforsk_on_joint'] = {f[1]: oa.count(B + ',funders.id:' + f[0].rsplit('/', 1)[-1]) for f in out['nordforsk_ids'][:2]}
ids = {}
for name in ['Aarhus University', 'Greenland Institute of Natural Resources', 'University of Manitoba']:
    x = oa.get('/institutions', search=name, per_page=1)['results'][0]
    ids[name] = (x['id'].rsplit('/', 1)[-1], x['display_name'])
out['asp_ids'] = ids
man, aar, gin = ids['University of Manitoba'][0], ids['Aarhus University'][0], ids['Greenland Institute of Natural Resources'][0]
out['manitoba_x_aarhus_or_ginr'] = {y: oa.count(f'type:article,publication_year:{y},institutions.id:{man},institutions.id:{aar}|{gin}') for y in range(2005, 2026)}
# Arctic only, against a comparator: Manitoba's Arctic articles with other Nordic institutions (not Aarhus or GINR)
out['arctic_manitoba_x_asp'] = {y: oa.count(f'type:article,publication_year:{y},{Q},institutions.id:{man},institutions.id:{aar}|{gin}') for y in range(2005, 2026)}
out['arctic_manitoba_x_nordic_all'] = {y: oa.count(f'type:article,publication_year:{y},{Q},institutions.id:{man},institutions.country_code:{NORDIC}') for y in range(2005, 2026)}
json.dump(out, open('../results/check_programmes.json', 'w'))
print(json.dumps(out, indent=0)[:2000])
