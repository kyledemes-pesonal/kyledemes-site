"""Step 2: download GROBID TEI (content.openalex.org, same endpoint as scripts/fetch_acks.py) for the first K works with
grobid_xml in each stratum's shuffled order. Raw TEI cached gzipped in the session scratchpad (not kept with the project).
usage: fetch_tei.py <K> <cache_dir>"""
import csv, gzip, os, sys, time, urllib.request, concurrent.futures as cf, collections
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'scripts'))
import oa
HERE = os.path.dirname(os.path.abspath(__file__))
K = int(sys.argv[1]); CACHE = sys.argv[2]; os.makedirs(CACHE, exist_ok=True)
R = [r for r in csv.DictReader(open(f'{HERE}/candidates.csv')) if r['has_grobid'] == '1']
by = collections.defaultdict(list)
for r in sorted(R, key=lambda r: int(r['rank'])): by[r['stratum']].append(r['work_id'])
todo = [w for s in by for w in by[s][:K]]
def get(wid):
    p = f'{CACHE}/{wid}.xml.gz'
    if os.path.exists(p): return wid, 'cached'
    for i in range(3):
        try:
            x = urllib.request.urlopen(f'https://content.openalex.org/works/{wid}.grobid-xml?api_key={oa.KEY}', timeout=90).read()
            with gzip.open(p, 'wb') as fh: fh.write(x)
            return wid, 'ok'
        except Exception as e:
            err = repr(e)[:80]; time.sleep(3 * (i + 1))
    return wid, 'ERR ' + err
c = collections.Counter(); t0 = time.time()
with cf.ThreadPoolExecutor(4) as ex:
    for n, (wid, st) in enumerate(ex.map(get, todo)):
        c[st.split()[0]] += 1
        if st.startswith('ERR'): print(wid, st, flush=True)
        if n % 100 == 0: print(n, len(todo), dict(c), round(time.time() - t0), 's', flush=True)
print('done', dict(c), round(time.time() - t0), 's')
