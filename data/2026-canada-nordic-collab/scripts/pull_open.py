"""Open access status of 2024 articles by country (Canada, each Nordic country, comparators), and the share with a
copy in a repository. Output ../results/open.json"""
import json, oa
C = ['CA', 'DK', 'FI', 'IS', 'NO', 'SE', 'US', 'GB', 'DE', 'FR', 'NL', 'AU', 'CH']
res = {}
for c in C:
    f = f'type:article,publication_year:2024,institutions.country_code:{c}'
    res[c] = {'total': oa.count(f), 'oa_status': {x['key']: x['count'] for x in oa.group(f, 'oa_status')},
              'repository_copy': oa.count(f + ',locations.source.type:repository')}
json.dump(res, open('../results/open.json', 'w'))
for c, r in res.items():
    t = r['total']; s = r['oa_status']
    print(c, t, 'open', f"{100*(t-s.get('closed',0))/t:.0f}%", ' '.join(f"{k}:{100*v/t:.0f}" for k, v in sorted(s.items())), 'repo', f"{100*r['repository_copy']/t:.0f}%")
