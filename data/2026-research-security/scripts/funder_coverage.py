"""Funder-metadata coverage on Canada-China articles (review check). Output ../results/funder_coverage.json"""
import json, oa
base = 'type:article,institutions.country_code:CA,institutions.country_code:CN,publication_year:2015-2025'
FUND = 'F4320334593|F4320334506|F4320334617|F7697234222|F4320319952|F4320320995'
def g(f): return {x['key']: x['count'] for x in oa.group(f, 'publication_year')}
csc = oa.get('/funders', search='China Scholarship Council')['results'][0]['id'].rsplit('/',1)[-1]
out = {'tot': g(base), 'csc_id': csc, 'csc': g(base + f',funders.id:{csc}'), 'canada': g(base + f',funders.id:{FUND}')}
for cand in ['funders.id:!null', 'has_funders:true', 'funders.count:>0']:
    try: out['any'] = g(base + ',' + cand); out['any_filter'] = cand; break
    except Exception as e: print('no', cand)
json.dump(out, open('../results/funder_coverage.json', 'w'))
for y in sorted(out['tot']):
    t = out['tot'][y]; a = out.get('any', {}).get(y, 0)
    print(y, t, 'any %.1f' % (100*a/t), 'csc %.1f' % (100*out['csc'].get(y,0)/t), 'canada|any %.1f' % (100*out['canada'].get(y,0)/a if a else 0))
print(out.get('any_filter'))
