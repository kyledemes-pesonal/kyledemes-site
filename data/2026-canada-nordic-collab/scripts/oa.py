import os, json, time, hashlib, urllib.parse, urllib.request, urllib.error
KEY = os.environ.get('OPENALEX_API_KEY')  # optional; set it for higher rate limits
BASE = 'https://api.openalex.org'
CACHE = os.path.join(os.path.dirname(__file__), '..', 'cache')  # local cache of raw responses (not published)
os.makedirs(CACHE, exist_ok=True)
def get(path, **params):
    url = BASE + path + '?' + urllib.parse.urlencode(params)
    fn = os.path.join(CACHE, hashlib.sha1(url.encode()).hexdigest() + '.json')
    if os.path.exists(fn):
        return json.load(open(fn))
    full = url + ('&api_key=' + KEY if KEY else '')
    err = None
    for attempt in range(8):
        try:
            req = urllib.request.Request(full, headers={'User-Agent': 'canada-nordic-analysis/1.0'})
            with urllib.request.urlopen(req, timeout=120) as r:
                data = json.loads(r.read())
            json.dump(data, open(fn, 'w'))
            return data
        except urllib.error.HTTPError as e:
            err = e
            if e.code in (400, 403, 404): raise  # bad filter: no point retrying
            time.sleep((15 if e.code == 429 else 3) * (attempt + 1))
        except Exception as e:
            err = e
            time.sleep(3 * (attempt + 1))
    raise err
def count(filt):
    return get('/works', filter=filt, per_page=1)['meta']['count']
def group(filt, by):
    return get('/works', filter=filt, group_by=by)['group_by']
