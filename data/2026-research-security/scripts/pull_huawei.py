"""Huawei in Canadian research papers (all work types), by Canadian institution and year, 2012-2025.
(a) credits Huawei as a funder (funders.id F4320322183); (b) has a Huawei-affiliated co-author (any Huawei company
record). Grouped by authorships.institutions.lineage, Canadian institutions kept. Output ../results/huawei_papers.json"""
import json, concurrent.futures as cf, oa
S = lambda u: u.rsplit('/', 1)[-1]
H = 'I2250955327|I4210123571|I4210115038|I4210129353|I4210146936|I4210159102|I4210166625|I4210160618|I4405252550'
SETS = {'funder': 'funders.id:F4320322183', 'coauthor': f'authorships.institutions.lineage:{H}'}
def job(k, y):
    f = f'institutions.country_code:CA,{SETS[k]},publication_year:{y}'
    out, cur = {}, '*'
    while cur:
        r = oa.get('/works', filter=f, group_by='authorships.institutions.lineage', per_page=200, cursor=cur)
        for x in r['group_by']: out[S(x['key'])] = x['count']
        cur = r['meta'].get('next_cursor') if r['group_by'] else None
    tot = oa.count(f)
    return k, y, out, tot
res = {k: {} for k in SETS}; tots = {k: {} for k in SETS}
with cf.ThreadPoolExecutor(4) as ex:
    for k, y, d, t in ex.map(lambda j: job(*j), [(k, y) for k in SETS for y in range(2012, 2026)]):
        res[k][str(y)] = d; tots[k][str(y)] = t
ids = sorted({i for k in res for d in res[k].values() for i in d})
names = {}
for i in range(0, len(ids), 100):
    r = oa.get('/institutions', filter='openalex:' + '|'.join(ids[i:i+100]), per_page=100, select='id,display_name,country_code,geo')
    for x in r['results']:
        if x.get('country_code') == 'CA': names[S(x['id'])] = [x['display_name'], (x.get('geo') or {}).get('region')]
json.dump({'by_inst': res, 'totals': tots, 'ca_institutions': names}, open('../results/huawei_papers.json', 'w'))
print('totals', tots)
for k in SETS:
    agg = {}
    for y, d in res[k].items():
        for i, n in d.items():
            if i in names: agg.setdefault(names[i][0], {})[y] = n
    top = sorted(agg.items(), key=lambda kv: -sum(kv[1].values()))[:15]
    print('==', k)
    for nm, d in top: print(f"{nm[:38]:38} " + ' '.join(f"{y[2:]}:{d.get(y,0)}" for y in [str(x) for x in range(2014, 2026)]))
