"""Country-pair co-authorship counts by year from the OpenAlex API.
For each focal country f, spec s, year t: group_by institutions.country_code on works
with an author at an institution in f -> count of works co-authored with every partner p
(p == f gives f's total). Also world totals per country (for Salton's index).
Output: ../results/pairs.json  {spec: {focal: {year: {partner: count}}}, 'world': {spec: {year: {cc: count}}}}
"""
import json, sys, concurrent.futures as cf
import oa
FOCAL = ['CA','US','GB','AU','DE','FR','JP','NL']
SPECS = {
  'all':   'type:article',
  'small': 'type:article,authors_count:<21',      # excludes large team-science papers (>=21 authors)
  'core':  'type:article,primary_location.source.is_core:true',
}
YEARS = list(range(2010, 2026))
def yfilt(y):
    return f'publication_year:{y}' if isinstance(y, int) else y
def cc(k): return k.rsplit('/',1)[-1]
def pull(spec, focal, y):
    f = SPECS[spec] + ',' + yfilt(y) + (f',institutions.country_code:{focal}' if focal else '')
    g = oa.group(f, 'institutions.country_code')
    return spec, focal or 'WORLD', y, {cc(x['key']): x['count'] for x in g}
# 2026 year-to-date and same window in earlier years (Jan 1 - Oct 31)
YTD = {f'ytd{y}': f'from_publication_date:{y}-01-01,to_publication_date:{y}-10-31' for y in range(2019, 2027)}
jobs = [(s, f, y) for s in SPECS for f in FOCAL + [None] for y in YEARS]
jobs += [('all', f, v) for f in FOCAL + [None] for v in YTD.values()]
out = {}
inv = {v: k for k, v in YTD.items()}
with cf.ThreadPoolExecutor(4) as ex:
    for i, (s, f, y, d) in enumerate(ex.map(lambda j: pull(*j), jobs)):
        out.setdefault(s, {}).setdefault(f, {})[str(inv.get(y, y))] = d
        if i % 50 == 0: print(i, len(jobs), file=sys.stderr)
json.dump(out, open('../results/pairs.json', 'w'))
print('done', len(jobs))
