"""How open are tri-agency-funded papers when funding is detected the same way for open and closed papers?

OpenAlex finds funders in Crossref metadata and in a paper's full text, which it mostly has for open papers, so its
funder tags lean towards open papers. For random samples of about 1,600 Canadian papers with DOIs per year (same seed
every year), this looks each DOI up in Crossref and compares three views of "tri-agency funded":
  oa_tag         OpenAlex's funder tags
  crossref_name  a tri-agency name in the funders the publisher deposited with Crossref (same rule for open and closed)
  imputed        OpenAlex tags, plus an estimate of the tags OpenAlex would have found on closed papers with no
                 Crossref funder record (the tag rate seen on open papers with no record, scaled by the closed/open
                 ratio among papers that have one)
For each view: share of the sample that is funded, the funded papers' free-to-read share, and the gap to the rest.

Run from the data folder:  python3 checks/crossref_funder_sample.py [years ...]   (default: 2024 2025)
Writes checks/crossref_funder_sample.json (aggregates only). Crossref public REST API, 50 DOIs per request.
"""
import json, os, re, sys, time, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from oa import get, TRI, BASE

HERE = os.path.dirname(os.path.abspath(__file__))
TRI_IDS = set('https://openalex.org/' + x for x in TRI.split('|'))
PAT = re.compile(r'natural sciences and engineering research council|nserc|crsng|social sciences and humanities research council|sshrc|crsh|'
                 r'canadian institutes of health research|cihr|irsc|instituts de recherche en sant|conseil de recherches en sciences|'
                 r'canada research chair|chaires de recherche du canada|canada excellence research chair|canada first research excellence|'
                 r'apogée|apogee', re.I)
UA = {'User-Agent': 'field-notes-replication/1.0'}


def crossref_batch(dois):
    url = 'https://api.crossref.org/works?' + urllib.parse.urlencode(
        {'filter': ','.join('doi:' + d for d in dois), 'rows': 100, 'select': 'DOI,funder'})
    for i in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as r:
                return {it['DOI'].lower(): it.get('funder') or [] for it in json.load(r)['message']['items']}
        except Exception:
            time.sleep(3 * (i + 1))
    return None


def sample(year):
    works = []
    for page in range(1, 9):
        r = get('works', filter=f'{BASE},publication_year:{year},institutions.country_code:CA,has_doi:true', sample=1600,
                seed=2027, per_page=200, page=page, select='id,doi,open_access,funders,has_fulltext')
        works += r['results']
    dois = [w['doi'].replace('https://doi.org/', '').lower() for w in works]
    with ThreadPoolExecutor(3) as ex:
        res = list(ex.map(crossref_batch, [dois[i:i + 50] for i in range(0, len(dois), 50)]))
    cr = {}
    for x in res:
        if x:
            cr.update(x)
    return [{'oa_status': w['open_access']['oa_status'],
             'oa_tag': any(f['id'] in TRI_IDS for f in w.get('funders') or []),
             'cr_found': cr.get(d) is not None, 'cr_has_funder': bool(cr.get(d)),
             'cr_tag': bool(cr.get(d)) and any(PAT.search(f.get('name', '') or '') for f in cr[d])}
            for w, d in zip(works, dois)]


def analyze(rows):
    rows = [r for r in rows if r['cr_found']]
    op = lambda r: r['oa_status'] != 'closed'
    n = len(rows); O = [r for r in rows if op(r)]; C = [r for r in rows if not op(r)]
    nat = 100 * len(O) / n

    def slice_stats(sel):
        f = [r for r in rows if sel(r)]; fo = sum(op(r) for r in f)
        return len(f), 100 * len(f) / n, 100 * fo / max(len(f), 1), nat - 100 * (len(O) - fo) / (n - len(f))

    def rate(s, sel=lambda r: r['oa_tag']):
        return sum(sel(r) for r in s) / max(len(s), 1)
    O_rec = [r for r in O if r['cr_has_funder']]; C_rec = [r for r in C if r['cr_has_funder']]
    O_norec = [r for r in O if not r['cr_has_funder']]; C_norec = [r for r in C if not r['cr_has_funder']]
    adj = rate(C_rec) / max(rate(O_rec), 1e-9)
    fo = sum(r['oa_tag'] for r in O)
    fc = sum(r['oa_tag'] for r in C_rec) + len(C_norec) * rate(O_norec) * adj
    a = slice_stats(lambda r: r['oa_tag']); b = slice_stats(lambda r: r['cr_tag'])
    return dict(n=n, national_open=round(nat, 1),
                oa_tag=dict(n=a[0], share=round(a[1], 1), funded_open=round(a[2], 1), lift=round(a[3], 1)),
                crossref_name=dict(n=b[0], share=round(b[1], 1), funded_open=round(b[2], 1), lift=round(b[3], 1)),
                imputed=dict(share=round(100 * (fo + fc) / n, 1), funded_open=round(100 * fo / (fo + fc), 1),
                             lift=round(nat - 100 * (len(O) - fo) / (n - fo - fc), 1)))


if __name__ == '__main__':
    years = [int(y) for y in sys.argv[1:]] or [2024, 2025]
    out = {}
    for y in years:
        out[str(y)] = analyze(sample(y))
        print(y, json.dumps(out[str(y)]), flush=True)
    with open(os.path.join(HERE, 'crossref_funder_sample.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=1)
