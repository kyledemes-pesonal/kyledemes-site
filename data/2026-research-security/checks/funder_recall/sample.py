"""Funder-field recall check, step 1: draw random samples per stratum from the local download (data/ca_works),
look up has_content / live funders via the API for a shuffled candidate list, keep those with GROBID TEI.
Output: candidates.csv (every looked-up candidate: stratum, id, year, has_grobid, field_tri local, field_tri live, first-author CN-only)
        population.json (stratum sizes and field_tri rate in the whole stratum)."""
import gzip, json, glob, random, csv, sys, os, collections
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'scripts'))
import oa
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'results', 'ca_works')
FUND = {'F4320334593', 'F4320334506', 'F4320334617', 'F7697234222', 'F4320319952', 'F4320320995'}
SEED = 20261120
N_LOOKUP = int(os.environ.get('N_LOOKUP', 1500))
P1, P2 = range(2018, 2021), range(2023, 2026)
strata = collections.defaultdict(list)
for fn in sorted(glob.glob(f'{DATA}/*.jsonl.gz')):
    for line in gzip.open(fn, 'rt'):
        w = json.loads(line); y = w['y']
        if y in P1: per = '2018-20'
        elif y in P2: per = '2023-25'
        else: continue
        cc = {c for a in w['a'] for c in a[3]}
        if 'CA' not in cc: continue
        if 'CN' in cc: grp = 'CA-CN'
        elif 'US' in cc: grp = 'CA-US'
        else: continue
        first_cn_only = bool(w['a']) and w['a'][0][3] == ['CN']
        strata[f'{grp} {per}'].append((w['w'], y, int(bool(set(w['f']) & FUND)), int(first_cn_only)))
pop = {}
rng = random.Random(SEED)
rows = []
for s in sorted(strata):
    L = strata[s]
    pop[s] = {'n': len(L), 'field_tri': sum(x[2] for x in L), 'field_tri_rate': sum(x[2] for x in L) / len(L),
              'first_cn_only': sum(x[3] for x in L)}
    L = sorted(L); rng.shuffle(L)
    cand = L[:N_LOOKUP]
    for i in range(0, len(cand), 50):
        chunk = cand[i:i + 50]
        r = oa.get('/works', filter='openalex:' + '|'.join(c[0] for c in chunk), per_page=50, select='id,has_content,funders,open_access')
        meta = {x['id'].rsplit('/', 1)[-1]: x for x in r['results']}
        for k, (wid, y, ft, fcn) in enumerate(chunk):
            m = meta.get(wid)
            live = None if m is None else int(any(f['id'].rsplit('/', 1)[-1] in FUND for f in m.get('funders') or []))
            hg = None if m is None else int(bool((m.get('has_content') or {}).get('grobid_xml')))
            oas = None if m is None else (m.get('open_access') or {}).get('oa_status')
            rows.append({'stratum': s, 'rank': i + k, 'work_id': wid, 'year': y, 'has_grobid': hg, 'field_tri_local': ft,
                         'field_tri_live': live, 'first_author_cn_only': fcn, 'oa_status': oas})
    print(s, pop[s], flush=True)
json.dump(pop, open(f'{HERE}/population.json', 'w'), indent=1)
with open(f'{HERE}/candidates.csv', 'w', newline='') as fh:
    wr = csv.DictWriter(fh, fieldnames=list(rows[0])); wr.writeheader(); wr.writerows(rows)
print('rows', len(rows))
