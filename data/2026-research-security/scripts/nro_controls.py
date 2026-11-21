"""Control pool: unlisted CN/IR/RU institutions of comparable research profile (top by works_count).

Reads results/nro_map.csv. Excludes:
  - every mapped NRO id (any confidence), its lineage children and listed alias units (child_ids),
  - any institution whose OpenAlex lineage contains one of those ids,
  - the nearest-parent proxies used for low-confidence rows (PLA, PLA Air Force, People's Armed
    Police, Ministry of Public Security, Russian MoD, Malek Ashtar Univ.) and anything under them,
    because they are military/security bodies and not clean controls.
Keeps types education / facility / government. Flags (doesn't drop) umbrella parents that have an
NRO somewhere below them (e.g. CAS above ICT/SIA, USTC above the Hefei microscale lab).
Output: results/nro_controls.csv
"""
import csv, sys
sys.path.insert(0, '.')
from oa import get

D = '../results/'
TARGET = {'CN': 250, 'IR': 60, 'RU': 60}
short = lambda x: x.split('/')[-1] if x else ''

rows = list(csv.DictReader(open(D + 'nro_map.csv')))
excl = set()
for r in rows:
    if r['openalex_id']:
        excl.add(r['openalex_id'])
    for part in r['child_ids'].replace('|', ';').split(';'):
        if part:
            excl.add(part)
nro_core = set(excl)  # ids treated as NRO (or NRO units / proxies)

# ids that have an NRO somewhere below them (for flagging umbrella parents)
nro_ancestors = {}
for oid in {r['openalex_id'] for r in rows if r['openalex_id'] and r['confidence'] in ('high', 'medium')}:
    i = get('/institutions/' + oid, select='id,lineage,display_name')
    for a in i['lineage']:
        a = short(a)
        if a != oid:
            nro_ancestors.setdefault(a, []).append(i['display_name'])

out = []
for cc, n in TARGET.items():
    kept, page = [], 1
    while len(kept) < n:
        res = get('/institutions', filter=f'country_code:{cc},type:education|facility|government',
                  sort='works_count:desc', per_page=200, page=page,
                  select='id,display_name,country_code,type,works_count,ror,lineage')['results']
        if not res:
            break
        for i in res:
            iid = short(i['id'])
            lin = {short(x) for x in i['lineage']}
            if iid in excl or lin & nro_core:
                continue
            kept.append(dict(id=iid, display_name=i['display_name'], country=cc, type=i['type'],
                             works_count=i['works_count'], ror=short(i['ror']),
                             parent_ids=';'.join(sorted(lin - {iid})),
                             has_nro_below=('; '.join(sorted(set(nro_ancestors.get(iid, [])))))))
            if len(kept) >= n:
                break
        page += 1
    out += kept
    print(cc, len(kept), 'min works', kept[-1]['works_count'])

with open(D + 'nro_controls.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['id', 'display_name', 'country', 'type', 'works_count', 'ror', 'parent_ids', 'has_nro_below'])
    w.writeheader(); w.writerows(out)
