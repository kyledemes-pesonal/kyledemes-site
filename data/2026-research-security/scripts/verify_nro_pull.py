"""Stage 1 of verify_nro: pull every candidate Canada-NRO article 2015-2025 (all team sizes) from the API
with full authorships, plus metadata for every institution involved. Cached in ../results/nro_verify_cache/.
Re-run safe (skips finished year-chunks)."""
import csv, json, gzip, os, sys, concurrent.futures as cf, oa
D = '../results'; C = f'{D}/nro_verify_cache'; os.makedirs(C, exist_ok=True)
S = lambda u: u.rsplit('/', 1)[-1] if u else None

def nro_ids():
    rows = [x for x in csv.DictReader(open(f'{D}/nro_map.csv')) if x['confidence'] in ('high', 'medium')]
    ids = []
    for x in rows:
        for i in [x['openalex_id']] + x['child_ids'].replace('|', ';').split(';'):
            i = i.strip()
            if i and i not in ids: ids.append(i)
    return rows, ids

def pull(job):
    y, k, chunk = job
    path = f'{C}/works_{y}_{k}.jsonl.gz'
    if os.path.exists(path + '.done'): return y, k, 'skip'
    filt = f'type:article,institutions.country_code:CA,publication_year:{y},authorships.institutions.lineage:' + '|'.join(chunk)
    cur, n = '*', 0
    with gzip.open(path, 'wt') as fh:
        while cur:
            r = oa.get('/works', filter=filt, per_page=200, cursor=cur,
                       select='id,doi,publication_year,title,type,is_paratext,is_retracted,authorships')
            for w in r['results']:
                fh.write(json.dumps(w, separators=(',', ':')) + '\n'); n += 1
            cur = r['meta'].get('next_cursor') if r['results'] else None
    open(path + '.done', 'w').write(str(n))
    return y, k, n

def inst_meta(ids):
    path = f'{C}/institutions.json'
    have = json.load(open(path)) if os.path.exists(path) else {}
    todo = [i for i in ids if i not in have]
    def one(chunk):
        r = oa.get('/institutions', filter='openalex_id:' + '|'.join(chunk), per_page=100,
                   select='id,display_name,display_name_alternatives,display_name_acronyms,international,country_code,lineage,geo,ror')
        return r['results']
    chunks = [todo[k:k+50] for k in range(0, len(todo), 50)]
    with cf.ThreadPoolExecutor(4) as ex:
        for res in ex.map(one, chunks):
            for x in res:
                have[S(x['id'])] = {'name': x['display_name'], 'alt': x.get('display_name_alternatives') or [],
                    'acr': x.get('display_name_acronyms') or [],
                    'intl': (x.get('international') or {}).get('display_name') or {},
                    'cc': x.get('country_code'), 'lineage': [S(l) for l in x.get('lineage') or []],
                    'city': (x.get('geo') or {}).get('city'), 'ror': x.get('ror')}
    json.dump(have, open(path, 'w'), ensure_ascii=False)
    return have

if __name__ == '__main__':
    rows, ids = nro_ids()
    jobs = [(y, k, ids[k:k+50]) for y in range(2015, 2026) for k in range(0, len(ids), 50)]
    with cf.ThreadPoolExecutor(4) as ex:
        for y, k, n in ex.map(pull, jobs): print(y, k, n, flush=True)
    # institutions: every institution on candidate works that has an NRO in its lineage or is CA, plus all NRO ids
    need = set(ids)
    import glob
    nset = set(ids)
    for p in glob.glob(f'{C}/works_*.jsonl.gz'):
        for l in gzip.open(p, 'rt'):
            w = json.loads(l)
            for a in w['authorships']:
                for i in a.get('institutions') or []:
                    lin = {S(x) for x in i.get('lineage') or []} | {S(i['id'])}
                    if lin & nset or i.get('country_code') == 'CA': need.add(S(i['id']))
    meta = inst_meta(sorted(x for x in need if x))
    print('institutions', len(meta))

def full_authorships():
    """List responses truncate authorships at 100; refetch those works singly (full list). Cache: full_<W>.json"""
    ids = set()
    for p in glob.glob(f'{C}/works_*.jsonl.gz'):
        for l in gzip.open(p, 'rt'):
            w = json.loads(l)
            if len(w['authorships']) >= 100: ids.add(S(w['id']))
    os.makedirs(f'{C}/full', exist_ok=True)
    todo = [i for i in ids if not os.path.exists(f'{C}/full/{i}.json')]
    def one(i):
        r = oa.get(f'/works/{i}', select='id,doi,publication_year,title,type,is_paratext,is_retracted,authorships')
        json.dump(r, open(f'{C}/full/{i}.json', 'w'))
        return i
    with cf.ThreadPoolExecutor(4) as ex:
        for _ in ex.map(one, todo): pass
    print('full authorships', len(ids), 'fetched', len(todo))
    return ids

if __name__ == '__main__':
    import glob
    full_authorships()
    # institution metadata for any new institutions in the full records
    need = set()
    rows, ids = nro_ids(); nset = set(ids)
    for p in glob.glob(f'{C}/full/*.json'):
        w = json.load(open(p))
        for a in w['authorships']:
            for i in a.get('institutions') or []:
                lin = {S(x) for x in i.get('lineage') or []} | {S(i['id'])}
                if lin & nset or i.get('country_code') == 'CA': need.add(S(i['id']))
    print('institutions', len(inst_meta(sorted(x for x in need if x))))
