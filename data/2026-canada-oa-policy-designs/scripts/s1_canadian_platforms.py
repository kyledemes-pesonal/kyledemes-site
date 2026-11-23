"""Baseline for the 'trusted Canadian platform' route: tri-agency papers (Canadian author) whose journal's publisher is
Canadian (publisher country_codes includes CA), by OA status, 2023-2025. Upper bound on that route: the policy does not
define 'trusted Canadian platform'."""
from oa import *
out = {}
pubcc = {}
for y in (2023, 2024, 2025):
    f = f'{BASE},publication_year:{y},institutions.country_code:CA,funders.id:{TRI}'
    r = get('works', filter=f, group_by='primary_location.source.publisher_lineage,oa_status', per_page=200)
    rows = {}
    for g in r['group_by']:
        rows[g['key'].rsplit('/', 1)[-1]] = {'name': g['key_display_name'], 'n': g['count'], **{s['key']: s['count'] for s in g['groups']}}
    ids = [k for k in rows if k not in pubcc and k.startswith('P')]
    for i in range(0, len(ids), 50):
        rr = get('publishers', filter='ids.openalex:' + '|'.join(ids[i:i+50]), per_page=50, select='id,country_codes')
        for p in rr['results']: pubcc[p['id'].rsplit('/', 1)[-1]] = p.get('country_codes') or []
    ca = {k: v for k, v in rows.items() if 'CA' in pubcc.get(k, [])}
    tot = count(f)
    n = sum(v['n'] for v in ca.values()); op = sum(v['n'] - v.get('closed', 0) for v in ca.values())
    out[y] = {'tri_ca_total': tot, 'canadian_publisher_papers': n, 'canadian_publisher_open': op,
              'publishers': {k: v for k, v in sorted(ca.items(), key=lambda x: -x[1]['n'])}}
    print(y, tot, n, op, [(v['name'], v['n']) for v in list(out[y]['publishers'].values())[:6]])
save('s1_canadian_platforms.json', out)
