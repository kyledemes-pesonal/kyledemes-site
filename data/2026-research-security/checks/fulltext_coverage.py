"""Check 5: full-text coverage of Canadian articles, 2016-2025, under each content filter the API accepts."""
import concurrent.futures as cf
import oax
BASE = 'type:article,institutions.country_code:CA,publication_year:2016-2025'
CANDIDATES = ['has_fulltext:true', 'has_content.pdf:true', 'has_content.grobid_xml:true', 'has_content.pdf:true,has_content.grobid_xml:true',
              'has_fulltext:true,has_content.grobid_xml:true', 'has_fulltext:true,has_content.grobid_xml:false',
              'has_content.grobid_xml:true,has_fulltext:false', 'fulltext_origin:pdf', 'fulltext_origin:ngrams', 'has_ngrams:true',
              'open_access.is_oa:true', 'has_pdf_url:true']
accepted = {}
for c in CANDIDATES:
    try:
        accepted[c] = oax.group(BASE + ',' + c, 'publication_year')
    except Exception as e:
        accepted[c] = {'error': str(e)[:300]}
tot = oax.group(BASE, 'publication_year')
years = [str(y) for y in range(2016, 2026)]
print('CA type:article totals', {y: tot.get(y) for y in years}, 'sum', sum(tot.get(y, 0) for y in years))
for c, g in accepted.items():
    if 'error' in g:
        print(f'{c:50} REJECTED: {g["error"][:160]}')
        continue
    s = sum(g.get(y, 0) for y in years); T = sum(tot.get(y, 0) for y in years)
    print(f'{c:50} all {100*s/T:5.1f}%  ' + ' '.join(f'{y[2:]}:{100*g.get(y,0)/tot[y]:4.1f}' for y in years))
# all types, as used by the Huawei candidate search (huawei_national.py had no type filter)
BA = 'institutions.country_code:CA,publication_year:2016-2025'
ta = oax.group(BA, 'publication_year')
for c in ['has_fulltext:true', 'has_content.grobid_xml:true', 'has_content.pdf:true']:
    try:
        g = oax.group(BA + ',' + c, 'publication_year')
        s = sum(g.get(y, 0) for y in years); T = sum(ta.get(y, 0) for y in years)
        print(f'ALL TYPES {c:40} all {100*s/T:5.1f}%  ' + ' '.join(f'{y[2:]}:{100*g.get(y,0)/ta[y]:4.1f}' for y in years))
    except Exception as e:
        print('ALL TYPES', c, 'REJECTED', str(e)[:160])
oax.dump({'totals': tot, 'filters': accepted, 'all_types_totals': ta}, 'fulltext_coverage.json')
