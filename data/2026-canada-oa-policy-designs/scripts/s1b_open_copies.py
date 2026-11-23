"""Open copies vs records in Canadian repositories for tri-agency-funded Canadian papers, 2016-2025 (23 Nov 2026).

A filter on locations.source.id (the monitor's list of Canadian repositories) matches any location at those sources,
including records with no open file. The 2026 policy asks for an open copy, so chart 2 now
plots papers with at least one is_oa location at one of those sources. Cursor-pages every matching work (select
id,locations) and counts both. Denominator: tri-agency x Canada papers, same day.
Run: python3 scripts/s1b_open_copies.py  ->  results/s1b_open_copies.json
"""
from oa import get, TRI, BASE, save, carepo_ids

ids = carepo_ids()
S = {'https://openalex.org/' + i for i in ids}
out = {'n_repositories': len(ids)}
for y in range(2016, 2026):
    base = f"{BASE},publication_year:{y},institutions.country_code:CA,funders.id:{TRI}"
    f = base + ",locations.source.id:" + '|'.join(ids)
    cur, rec, opn = '*', 0, 0
    while cur:
        r = get('works', filter=f, per_page=200, cursor=cur, select='id,locations')
        if not r['results']:
            break
        for w in r['results']:
            rec += 1
            opn += any(l.get('is_oa') for l in w['locations'] if (l.get('source') or {}).get('id') in S)
        cur = r['meta'].get('next_cursor')
    n = get('works', filter=base, per_page=1)['meta']['count']
    out[y] = {'tri_ca': n, 'with_record': rec, 'with_open_copy': opn,
              'pct_record': round(100 * rec / n, 1), 'pct_open_copy': round(100 * opn / n, 1)}
    print(y, out[y])
save('s1b_open_copies.json', out)
