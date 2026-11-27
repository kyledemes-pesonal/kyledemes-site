"""Articles 2021-2025 by primary-topic field and subfield for Canada, the Nordic region, Canada x Nordic (all, and
papers with at most 10 countries) and the world. Subfields are pulled field by field (single group_by pages; cursor
paging of group_by dropped groups in Nov 2026). Output ../results/subfields.json"""
import json, oa
from defs import NORDIC as N
B = 'type:article,publication_year:2021-2025'
SETS = {'CA': f'{B},institutions.country_code:CA', 'NORDIC': f'{B},institutions.country_code:{N}',
        'CA_NORDIC': f'{B},institutions.country_code:CA,institutions.country_code:{N}',
        'CA_NORDIC_le10': f'{B},institutions.country_code:CA,institutions.country_code:{N},countries_distinct_count:<11',
        'CA_le10': f'{B},institutions.country_code:CA,countries_distinct_count:<11',
        'WORLD': B}
def grp(f, by):
    r = oa.get('/works', filter=f, group_by=by, per_page=200)
    assert r['meta'].get('groups_count', 0) < 200, 'more than one page'
    return {x['key'].rsplit('/', 1)[-1]: [x['key_display_name'], x['count']] for x in r['group_by']}
res = {}
for k, f in SETS.items():
    fields = grp(f, 'primary_topic.field.id')
    sub = {}
    for fid in fields:
        sub.update(grp(f'{f},primary_topic.field.id:{fid}', 'primary_topic.subfield.id'))
    res[k] = {'field': fields, 'subfield': sub, 'total': oa.count(f)}
    print(k, res[k]['total'], len(fields), len(sub), sum(v[1] for v in fields.values()), sum(v[1] for v in sub.values()))
json.dump(res, open('../results/subfields.json', 'w'))
