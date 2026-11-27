"""Institutions and funders on Canada x Nordic articles, 2021-2025 (all, and Arctic/northern only).
group_by pages are single pages of the top 200 by count (cursor paging of group_by dropped groups in Nov 2026).
Institutions: one query per Nordic country (Canada x that country), so each country's own institutions make its top 200.
Output ../results/institutions.json"""
import json, oa
from defs import NORDIC, Q
B = 'type:article,publication_year:2021-2025,institutions.country_code:CA'
def top(f, by):
    return [[x['key'].rsplit('/', 1)[-1], x['key_display_name'], x['count']]
            for x in oa.get('/works', filter=f, group_by=by, per_page=200)['group_by']]
def countries(ids):
    cc = {}
    for k in range(0, len(ids), 50):
        r = oa.get('/institutions', filter='openalex_id:' + '|'.join(ids[k:k + 50]), per_page=50, select='id,country_code,type')
        for x in r['results']:
            cc[x['id'].rsplit('/', 1)[-1]] = [x['country_code'], x['type']]
    return cc
res = {}
for name, extra in {'all': '', 'arctic': ',' + Q}.items():
    r = {'total': oa.count(f'{B},institutions.country_code:{NORDIC}{extra}'), 'by_country': {}}
    for c in ['CA'] + NORDIC.split('|'):
        f = f'{B},institutions.country_code:{NORDIC if c == "CA" else c}{extra}'
        inst = top(f, 'institutions.id')
        cc = countries([i[0] for i in inst])
        r['by_country'][c] = {'papers': oa.count(f), 'institutions': [i + cc.get(i[0], [None, None]) for i in inst if cc.get(i[0], [None])[0] == c]}
    r['funders'] = top(f'{B},institutions.country_code:{NORDIC}{extra}', 'funders.id')
    r['funders_le10'] = top(f'{B},institutions.country_code:{NORDIC},countries_distinct_count:<11{extra}', 'funders.id')
    res[name] = r
json.dump(res, open('../results/institutions.json', 'w'))
