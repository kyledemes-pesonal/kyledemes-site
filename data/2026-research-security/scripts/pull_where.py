"""Where: U15 universities and fields. Canada-China co-authored articles in 2018-2020 vs 2023-2025.
Output ../results/where.json"""
import json, concurrent.futures as cf, oa
U15 = ['University of British Columbia','University of Alberta','University of Calgary','University of Saskatchewan',
       'University of Manitoba','University of Waterloo','Western University','McMaster University','University of Toronto',
       "Queen's University",'University of Ottawa','McGill University','Université de Montréal','Université Laval','Dalhousie University']
def find(name):
    r = oa.get('/institutions', search=name, filter='country_code:CA')['results'][0]
    return name, r['id'].rsplit('/',1)[-1], r['display_name']
with cf.ThreadPoolExecutor(4) as ex: ids = list(ex.map(find, U15))
P = {'pre': '2018-2020', 'post': '2023-2025'}
def job(iid, per, p):
    f = f'type:article,authorships.institutions.lineage:{iid},publication_year:{P[per]}' + (f',institutions.country_code:{p}' if p else '')
    return iid, per, p or 'ALL', oa.count(f)
jobs = [(i, per, p) for _, i, _ in ids for per in P for p in [None,'CN','HK','IR','RU','US','GB']]
out = {'ids': ids, 'inst': {}}
with cf.ThreadPoolExecutor(4) as ex:
    for i, per, p, n in ex.map(lambda j: job(*j), jobs):
        out['inst'].setdefault(i, {}).setdefault(per, {})[p] = n
# fields
def fjob(per, p):
    f = f'type:article,institutions.country_code:CA,publication_year:{P[per]}' + (f',institutions.country_code:{p}' if p else '')
    return per, p or 'ALL', {x['key_display_name']: x['count'] for x in oa.group(f, 'primary_topic.field.id')}
with cf.ThreadPoolExecutor(4) as ex:
    for per, p, d in ex.map(lambda j: fjob(*j), [(per, p) for per in P for p in [None,'CN']]):
        out.setdefault('fields', {}).setdefault(per, {})[p] = d
json.dump(out, open('../results/where.json','w'), indent=0)
for n, i, dn in ids:
    a = out['inst'][i]
    print(f"{dn[:30]:30} pre {a['pre']['CN']:5d}/{a['pre']['ALL']:6d}={100*a['pre']['CN']/a['pre']['ALL']:4.1f}%  post {a['post']['CN']:5d}/{a['post']['ALL']:6d}={100*a['post']['CN']/a['post']['ALL']:4.1f}%")
