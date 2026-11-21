"""Download every Canadian article 2015-2025 (authors_count < 51) from the OpenAlex API in compact form,
for the author panel and the scripts that read it. About 1.1 million works, roughly an hour; keep the output local
(it holds author IDs). One cursor stream per half-year, run in parallel.
Output: ../results/ca_works/<period>.jsonl.gz, one line per work:
  {"w": id, "y": year, "f": funders (short ids), "a": [[author_id, has_orcid, [lineage ids], [countries]], ...]}"""
import json, gzip, os, sys, time, concurrent.futures as cf, oa
OUT = '../results/ca_works'; os.makedirs(OUT, exist_ok=True)
BASE = 'type:article,institutions.country_code:CA,authors_count:<51'
S = lambda u: u.rsplit('/', 1)[-1] if u else None
periods = []
for y in range(2015, 2026):
    periods += [(f'{y}a', f'from_publication_date:{y}-01-01,to_publication_date:{y}-06-30'),
                (f'{y}b', f'from_publication_date:{y}-07-01,to_publication_date:{y}-12-31')]
if len(sys.argv) > 1:  # optional: only these half-years, e.g. python pull_ca_works.py 2025b (for a spot check)
    periods = [p for p in periods if p[0] in sys.argv[1:]]
def run(p):
    name, f = p; path = f'{OUT}/{name}.jsonl.gz'; done = f'{OUT}/{name}.done'
    if os.path.exists(done): return name, 'skip'
    cur, n = '*', 0
    with gzip.open(path, 'wt') as fh:
        while cur:
            r = oa.get('/works', filter=BASE + ',' + f, per_page=200, cursor=cur, select='id,publication_year,authorships,funders')
            for w in r['results']:
                a = []
                for au in w.get('authorships') or []:
                    lin = sorted({S(l) for i in au.get('institutions') or [] for l in (i.get('lineage') or [i.get('id')]) if l})
                    cc = sorted({i.get('country_code') for i in au.get('institutions') or [] if i.get('country_code')} | set(au.get('countries') or []))
                    a.append([S((au.get('author') or {}).get('id')), bool((au.get('author') or {}).get('orcid')), lin, cc])
                fh.write(json.dumps({'w': S(w['id']), 'y': w.get('publication_year'), 'f': [S(x['id']) for x in w.get('funders') or []], 'a': a}, separators=(',', ':')) + '\n')
                n += 1
            cur = r['meta'].get('next_cursor') if r['results'] else None
    open(done, 'w').write(str(n))
    return name, n
with cf.ThreadPoolExecutor(4) as ex:
    for name, n in ex.map(run, periods):
        print(time.strftime('%H:%M:%S'), name, n, flush=True)
print('ALL DONE')
