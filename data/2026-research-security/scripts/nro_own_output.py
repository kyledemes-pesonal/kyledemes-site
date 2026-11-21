"""Own article output of the listed Chinese organizations and of the control institutions, by year, 2015-2025.
Used by nro_funded_split.py to adjust for each group's growth worldwide.
Same groups and the same unit as that index: listed = high/medium CN rows of nro_map.csv plus their child_ids (114 IDs);
controls = CN rows of nro_controls.csv minus the CAS/USTC/MIIT umbrellas and rows with has_nro_below (247 IDs).
Own output of a group = sum over its IDs of type:article works with that ID in authorships.institutions.lineage
(institution-work links, so a work with two IDs counts twice, as in the published index).
Output ../results/nro_own_output.json {'own_nro': {year: n}, 'own_ctl': {year: n}, 'n_nro_ids', 'n_ctl'}"""
import csv, json, concurrent.futures as cf, oa
nro = [r for r in csv.DictReader(open('../results/nro_map.csv')) if r['confidence'] in ('high', 'medium') and r['country'] == 'CN']
N = set()
for r in nro:
    N.add(r['openalex_id'])
    N |= {c.strip() for c in r['child_ids'].replace('|', ';').split(';') if c.strip()}
UMB = {'Chinese Academy of Sciences', 'Ministry of Industry and Information Technology', 'University of Science and Technology of China'}
C = {r['id'] for r in csv.DictReader(open('../results/nro_controls.csv'))
     if r['country'] == 'CN' and r['display_name'] not in UMB and r['has_nro_below'] in ('', 'False', 'false', '0')}
def own(i):
    g = oa.group(f'type:article,authorships.institutions.lineage:{i},publication_year:2015-2025', 'publication_year')
    return i, {x['key']: x['count'] for x in g}
res = {}
with cf.ThreadPoolExecutor(4) as ex:
    for i, d in ex.map(own, sorted(N | C)): res[i] = d
Y = [str(y) for y in range(2015, 2026)]
out = {'n_nro_ids': len(N), 'n_ctl': len(C),
       'own_nro': {t: sum(res[i].get(t, 0) for i in N) for t in Y}, 'own_ctl': {t: sum(res[i].get(t, 0) for i in C) for t in Y}}
json.dump(out, open('../results/nro_own_output.json', 'w'), indent=1)
print(json.dumps(out))
