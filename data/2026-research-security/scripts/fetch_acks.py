"""Fetch GROBID XML from the OpenAlex content API for a list of works and extract the acknowledgement/funding
sections. usage: fetch_acks.py <works.json> <out.jsonl>"""
import os, json, sys, re, time, urllib.request, concurrent.futures as cf
KEY = os.environ['OPENALEX_API_KEY']  # the content API needs a key
ws = json.load(open(sys.argv[1]))
def get(w):
    wid = w['id'].rsplit('/', 1)[-1]
    if not (w.get('has_content') or {}).get('grobid_xml'): return None
    for i in range(3):
        try:
            x = urllib.request.urlopen(f'https://content.openalex.org/works/{wid}.grobid-xml?api_key={KEY}', timeout=60).read().decode('utf-8', 'ignore'); break
        except Exception as e:
            x = None; time.sleep(2)
    if not x: return {'w': wid, 'err': True}
    parts = re.findall(r'<div[^>]*type="(?:acknowledgement|funding)"[^>]*>(.*?)</div>', x, re.S)
    parts += re.findall(r'<funder[^>]*>(.*?)</funder>', x, re.S)
    txt = re.sub(r'<[^>]+>', ' ', ' '.join(parts)); txt = re.sub(r'\s+', ' ', txt).strip()
    if not txt:  # fall back: any paragraph mentioning support/funded
        txt = ' '.join(re.sub(r'<[^>]+>', ' ', p) for p in re.findall(r'<p>(.*?)</p>', x, re.S) if re.search(r'support|fund|grant|thank', p, re.I))[-1500:]
    return {'w': wid, 'y': w.get('publication_year'), 'title': w.get('title'), 'ack': txt}
with cf.ThreadPoolExecutor(4) as ex, open(sys.argv[2], 'w') as fh:
    for r in ex.map(get, ws):
        if r: fh.write(json.dumps(r, ensure_ascii=False) + '\n')
