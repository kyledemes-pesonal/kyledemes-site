"""Read the passages around each OpenAlex mention, for works whose title and abstract don't name OpenAlex.

For every candidate outside the title/abstract set, try the open copies listed in the work's OpenAlex `locations`
(repositories first, then publisher PDFs, then HTML landing pages), extract the text (PyMuPDF for PDFs), and keep
up to 6 passages of +-500 characters around matches of /open ?alex/i. Full texts are not kept, only passages.
Polite: one request at a time per host, 3 s apart (arXiv asks for this), 8 hosts in parallel. Atypon Literatum hosts
(Wiley, T&F, SAGE, ACS ...) are skipped: they block an IP after bursts (memory atypon-sites-block-burst-fetching).
Output: data/passages.jsonl, one row per work, resumable. Run with ~/.venvs/pdfread/bin/python.
"""
import glob, html, json, os, re, sys, threading, time, urllib.error, urllib.parse, urllib.request
import fitz  # PyMuPDF

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
OUT = os.path.join(DATA, 'passages.jsonl')
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) field-notes-research/1.0'
ATYPON = ('onlinelibrary.wiley.com', 'tandfonline.com', 'journals.sagepub.com', 'pubs.acs.org', 'cdnsciencepub.com',
          'science.org', 'ascelibrary.org', 'liebertpub.com', 'journals.physiology.org', 'annualreviews.org',
          'nejm.org', 'journals.asm.org', 'ahajournals.org', 'pubs.rsna.org', 'emerald.com', 'aeaweb.org',
          'journals.uchicago.edu', 'muse.jhu.edu', 'agupubs', 'physiology.org', 'futuremedicine.com', 'jstor.org',
          'sciencedirect.com', 'researchgate.net')  # last two: bot walls, never return the text
REPO_FIRST = ('arxiv.org', 'europepmc.org', 'ncbi.nlm.nih.gov', 'zenodo.org', 'hal.science', 'osf.io', 'biorxiv.org',
              'medrxiv.org', 'ssrn.com', 'researchsquare.com', 'preprints.org', 'aclanthology.org', 'figshare')
PAT = re.compile(r'open\s?alex', re.I)
REFS = re.compile(r'\n\s*(references|bibliography|works cited|literature cited|referências|referencias|références|literatur)\s*\n', re.I)


def host(u):
    return u.split('/')[2].lower() if u and u.count('/') >= 2 else ''


def candidate_urls(w):
    pdfs, pages = [], []
    for loc in [w.get('best_oa_location') or {}] + (w.get('locations') or []):
        p, l = loc.get('pdf_url'), loc.get('landing_page_url')
        if p and p not in pdfs:
            pdfs.append(p)
        if l and l not in pages and loc.get('is_oa'):
            pages.append(l)
    pdfs.sort(key=lambda u: 0 if any(h in u for h in REPO_FIRST) else 1)
    urls = [u for u in pdfs + pages if not any(a in host(u) for a in ATYPON)]
    return urls[:4]


def text_of(body):
    if body[:5] == b'%PDF-':
        with fitz.open(stream=body, filetype='pdf') as doc:
            return '\n'.join(p.get_text() for p in doc), 'pdf'
    t = body.decode('utf-8', 'ignore')
    t = re.sub(r'(?is)<(script|style|nav|header|footer)[^>]*>.*?</\1>', ' ', t)
    t = re.sub(r'(?i)<(br|p|div|h\d|li|tr)[^>]*>', '\n', t)
    return html.unescape(re.sub(r'<[^>]+>', ' ', t)), 'html'


def passages(text):
    hits = [m.start() for m in PAT.finditer(text)]
    refs = [m.start() for m in REFS.finditer(text)]
    ref_start = refs[-1] if refs and refs[-1] > len(text) * 0.5 else None
    spans = []
    for h in hits:
        a, b = max(0, h - 500), min(len(text), h + 500)
        if spans and a <= spans[-1][1]:
            spans[-1][1] = b
        else:
            spans.append([a, b])
    body_hits = [h for h in hits if ref_start is None or h < ref_start]
    # prefer passages in the body; keep one reference-list passage if that is all there is
    chosen = [s for s in spans if ref_start is None or s[0] < ref_start][:6] or spans[:2]
    return {'n_mentions': len(hits), 'n_body_mentions': len(body_hits), 'has_refs_heading': ref_start is not None,
            'passages': [re.sub(r'\s+', ' ', text[a:b]) for a, b in chosen], 'text_chars': len(text)}


lock = threading.Lock()
last_hit = {}
busy = set()


def fetch(url):
    h = host(url)
    if h in ('doi.org', 'dx.doi.org'):  # a resolver: the redirect targets are many different hosts
        h = url
    while True:
        with lock:
            if h not in busy and time.time() - last_hit.get(h, 0) >= 3:
                busy.add(h)
                break
        time.sleep(0.2)
    try:
        req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'application/pdf,text/html;q=0.9,*/*;q=0.5'})
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                return r.read(40_000_000)
        except urllib.error.HTTPError as e:  # urllib does not follow 308
            if e.code in (307, 308) and e.headers.get('Location'):
                loc = urllib.parse.urljoin(url, e.headers['Location'])
                with urllib.request.urlopen(urllib.request.Request(loc, headers=req.headers), timeout=25) as r:
                    return r.read(40_000_000)
            raise
    finally:
        with lock:
            busy.discard(h)
            last_hit[h] = time.time()


def work_job(w):
    tried = []
    for u in candidate_urls(w):
        try:
            body = fetch(u)
            text, kind = text_of(body)
            if len(text) < 2000:
                tried.append([u, 'short'])
                continue
            p = passages(text)
            if p['n_mentions'] == 0 and kind == 'html':
                tried.append([u, 'html-no-mention'])
                continue
            return dict(id=w['id'], url=u, kind=kind, status='ok', tried=tried, **p)
        except Exception as e:  # noqa: BLE001
            tried.append([u, str(e)[:80]])
    return dict(id=w['id'], status='no_text', tried=tried)


def main():
    recs, sets = {}, {}
    for s in ('cites', 'titleabs', 'fulltext'):
        ids = set()
        for f in glob.glob(os.path.join(DATA, 'raw', s, 'page_*.json')):
            for w in json.load(open(f))['results']:
                ids.add(w['id'])
                recs[w['id']] = w
        sets[s] = ids
    todo = sorted((sets['fulltext'] | sets['cites']) - sets['titleabs'])
    done = set()
    if os.path.exists(OUT):
        done = {json.loads(l)['id'] for l in open(OUT)}
    todo = [i for i in todo if i not in done]
    print('to fetch', len(todo), 'already', len(done), flush=True)
    # round-robin across hosts so the workers rarely wait on the same one
    by_host = {}
    for i in todo:
        by_host.setdefault(host((candidate_urls(recs[i]) or [''])[0]), []).append(i)
    order, lists = [], sorted(by_host.values(), key=len, reverse=True)
    while any(lists):
        for l in lists:
            if l:
                order.append(l.pop())
    q, out_lock, n = order[::-1], threading.Lock(), [0]

    def worker():
        while True:
            with out_lock:
                if not q:
                    return
                i = q.pop()
            row = work_job(recs[i])
            with out_lock:
                with open(OUT, 'a') as f:
                    f.write(json.dumps(row, ensure_ascii=False) + '\n')
                n[0] += 1
                if n[0] % 100 == 0:
                    print(time.strftime('%H:%M:%S'), n[0], 'done', flush=True)

    ts = [threading.Thread(target=worker) for _ in range(int(sys.argv[1]) if len(sys.argv) > 1 else 8)]
    [t.start() for t in ts]
    [t.join() for t in ts]
    print('finished', flush=True)


if __name__ == '__main__':
    main()
