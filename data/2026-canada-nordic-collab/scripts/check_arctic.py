"""Checks on the Arctic set: domestic-only share of Canada's Arctic articles by year; Nordic share on papers with
<=10 countries. Output ../results/check_arctic.json (counts only).
Two title samples are written to ../cache/check_arctic_samples.json (local, not published): 25 works matching a bare
'sami' (why it isn't used: the given name Sami, Croatian 'sami') and 60 random Canadian Arctic-set articles from
2016-2025, read by hand for precision."""
import json, os, oa
from defs import Q, NORDIC
out = {}
samples = {}
for y in range(2010, 2026):
    f = f'type:article,publication_year:{y},{Q},institutions.country_code:CA'
    t = oa.count(f); dom = oa.count(f + ',countries_distinct_count:1')
    le = oa.count(f + ',countries_distinct_count:<11'); len_ = oa.count(f + f',countries_distinct_count:<11,institutions.country_code:{NORDIC}')
    out[y] = {'total': t, 'domestic': dom, 'le10': le, 'le10_nordic': len_}
    print(y, t, f'domestic {100*dom/t:.0f}%', f'nordic(le10) {100*len_/le:.1f}%')
r = oa.get('/works', filter='type:article,publication_year:2016-2025,title_and_abstract.search:sami', per_page=25, select='display_name', sample=25, seed=7)
samples['sami_bare_sample'] = [w['display_name'] for w in r['results']]
# precision sample: 60 random Canadian Arctic-set articles, titles only (kept local)
r = oa.get('/works', filter=f'type:article,publication_year:2016-2025,{Q},institutions.country_code:CA', per_page=60, select='display_name', sample=60, seed=11)
samples['ca_sample'] = [w['display_name'] for w in r['results']]
json.dump(out, open('../results/check_arctic.json', 'w'), ensure_ascii=False)
json.dump(samples, open(os.path.join(oa.CACHE, 'check_arctic_samples.json'), 'w'), ensure_ascii=False)
for t in samples['sami_bare_sample']: print(' -', (t or '')[:110])
for t in samples['ca_sample']: print(' *', (t or '')[:110])
