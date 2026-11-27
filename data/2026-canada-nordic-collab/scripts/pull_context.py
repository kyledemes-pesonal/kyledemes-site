"""Context numbers added after the verification pass (24 Nov 2026). Output ../results/context.json
- intl: share of Canadian articles with a co-author in another country, by year
- le10: share of Canadian articles with a co-author in each partner, papers with co-authors in 10 or fewer countries
- greenland_2021_2025: Greenland's articles 2021-2025 grouped by co-author country"""
import json, oa
from defs import NORDIC
out = {'intl': {}, 'le10': {}}
for y in range(2000, 2026):
    b = f'type:article,publication_year:{y},institutions.country_code:CA'
    out['intl'][y] = [oa.count(b + ',countries_distinct_count:>1'), oa.count(b)]
for y in (2000, 2010, 2020, 2025):
    b = f'type:article,publication_year:{y},institutions.country_code:CA,countries_distinct_count:<11'
    d = {'_total': oa.count(b), 'NORDIC': oa.count(b + f',institutions.country_code:{NORDIC}')}
    for c in ['US', 'CN', 'GB', 'DE', 'FR', 'AU', 'NL']:
        d[c] = oa.count(b + f',institutions.country_code:{c}')
    out['le10'][y] = d
f = 'type:article,publication_year:2021-2025,institutions.country_code:GL'
out['greenland_2021_2025'] = {x['key'].rsplit('/', 1)[-1]: x['count'] for x in oa.group(f, 'institutions.country_code')}
out['greenland_2021_2025']['_total'] = oa.count(f)
json.dump(out, open('../results/context.json', 'w'))
print('done')
