"""Were the 2018-20 cohort authors still publishing from Canada in 2023-25, and if not, where did they go?
Cohorts from author_panel.py (run with VERIFIED=1 first): A = Canadian authors on a verified listed-organization (NRO)
work in 2018-20; B = Canadian authors on a control-institution work in 2018-20 and no NRO work 2015-20.
Active = at least one Canadian-affiliated paper in 2023-25 in the local download. Inactive authors are looked up in
OpenAlex author records: last_known_institutions country and works in 2023-2025 (counts_by_year). A: all inactive;
B: random 1,600. Output ../results/panel_status.json (counts only; no author IDs)"""
import json, random, collections, concurrent.futures as cf, oa
P = json.load(open('../results/author_panel_verified.json'))['panel']
POST = ('2023', '2024', '2025')
status, inactive = {}, {}
for g in ('A', 'B'):
    act = [a for a, yrs in P[g].items() if sum((yrs.get(t) or [0])[0] for t in POST) > 0]
    inactive[g] = [a for a in P[g] if a not in set(act)]
    status[g] = {'cohort': len(P[g]), 'active_ca': len(act), 'inactive_ca': len(inactive[g]),
                 'active_share': round(len(act) / len(P[g]), 3)}
print(json.dumps(status))
random.seed(7)
groups = {'A': inactive['A'], 'B': random.sample(sorted(inactive['B']), min(1600, len(inactive['B'])))}  # sorted: same sample every run
def fetch(ids):
    r = oa.get('/authors', filter='openalex:' + '|'.join(ids), per_page=100, select='id,last_known_institutions,counts_by_year')
    return r['results']
out = {'status': status}
for g, ids in groups.items():
    batches = [ids[i:i+50] for i in range(0, len(ids), 50)]
    c = collections.Counter(); where = collections.Counter()
    with cf.ThreadPoolExecutor(4) as ex:
        for res in ex.map(fetch, batches):
            for a in res:
                recent = sum(y['works_count'] for y in a.get('counts_by_year') or [] if 2023 <= y['year'] <= 2025)
                cc = {i.get('country_code') for i in a.get('last_known_institutions') or []}
                if recent == 0: c['stopped_publishing'] += 1
                elif 'CA' in cc: c['publishing_ca_other'] += 1
                else:
                    c['moved_abroad'] += 1
                    for x in cc: where[x or '??'] += 1
    out[g] = {'checked': len(ids), **c, 'abroad_where': where.most_common(10)}
json.dump(out, open('../results/panel_status.json', 'w'), indent=1); print(json.dumps(out, indent=1))
