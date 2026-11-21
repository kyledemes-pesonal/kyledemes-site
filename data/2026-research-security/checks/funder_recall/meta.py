"""Step 4: for every candidate, OpenAlex DOI + live funders + awards (which funder each award number was attached to);
then Crossref's deposited funder list for (a) every downloaded work and (b) the first 250 non-full-text candidates per stratum.
Crossref is queried without any email/mailto. Output meta.jsonl, crossref.jsonl"""
import csv, json, os, sys, time, urllib.request, urllib.parse, concurrent.futures as cf, collections, glob
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'scripts'))
import oa
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = sys.argv[1]
C = list(csv.DictReader(open(f'{HERE}/candidates.csv')))
if not os.path.exists(f'{HERE}/meta.jsonl'):
    with open(f'{HERE}/meta.jsonl', 'w') as fh:
        for i in range(0, len(C), 50):
            ids = [c['work_id'] for c in C[i:i + 50]]
            r = oa.get('/works', filter='openalex:' + '|'.join(ids), per_page=50, select='id,doi,funders,awards')
            for x in r['results']:
                fh.write(json.dumps({'work_id': x['id'].rsplit('/', 1)[-1], 'doi': x.get('doi'),
                                     'funders': [[f['id'].rsplit('/', 1)[-1], f.get('display_name')] for f in x.get('funders') or []],
                                     'awards': [[a.get('funder_id', '').rsplit('/', 1)[-1] if a.get('funder_id') else None, a.get('funder_award_id')] for a in x.get('awards') or []]}) + '\n')
    print('meta done', flush=True)
M = {json.loads(l)['work_id']: json.loads(l) for l in open(f'{HERE}/meta.jsonl')}
fetched = {os.path.basename(p).split('.')[0] for p in glob.glob(f'{CACHE}/*.xml.gz')}
nonft = collections.defaultdict(list)
for c in sorted(C, key=lambda c: int(c['rank'])):
    if c['has_grobid'] == '0': nonft[c['stratum']].append(c['work_id'])
todo = sorted(fetched & set(M)) + [w for s in nonft for w in nonft[s][:250]]
done = set()
if os.path.exists(f'{HERE}/crossref.jsonl'):
    done = {json.loads(l)['work_id'] for l in open(f'{HERE}/crossref.jsonl')}
todo = [w for w in todo if w not in done and M.get(w, {}).get('doi')]
def get(wid):
    doi = M[wid]['doi'].replace('https://doi.org/', '')
    url = 'https://api.crossref.org/works/' + urllib.parse.quote(doi, safe='/')
    for i in range(4):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'openalex-funder-recall-check/1.0'})
            x = json.loads(urllib.request.urlopen(req, timeout=60).read())['message']
            return {'work_id': wid, 'ok': 1, 'member': x.get('member'), 'publisher': x.get('publisher'),
                    'funder': [[f.get('DOI'), f.get('name'), f.get('award') or []] for f in x.get('funder') or []]}
        except urllib.error.HTTPError as e:
            if e.code == 404: return {'work_id': wid, 'ok': 0, 'err': 404}
            time.sleep(3 * (i + 1))
        except Exception:
            time.sleep(3 * (i + 1))
    return {'work_id': wid, 'ok': 0, 'err': 'fail'}
t0 = time.time()
with cf.ThreadPoolExecutor(4) as ex, open(f'{HERE}/crossref.jsonl', 'a') as fh:
    for n, r in enumerate(ex.map(get, todo)):
        fh.write(json.dumps(r, ensure_ascii=False) + '\n')
        if n % 200 == 0: print(n, len(todo), round(time.time() - t0), 's', flush=True)
print('crossref done', len(todo))
