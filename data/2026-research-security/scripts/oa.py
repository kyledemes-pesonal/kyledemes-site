import os, re, json, time, urllib.parse, urllib.request
KEY = os.environ.get('OPENALEX_API_KEY')  # optional; set it for higher rate limits
BASE = 'https://api.openalex.org'
def get(path, **params):
    if KEY: params['api_key'] = KEY
    url = BASE + path + '?' + urllib.parse.urlencode(params)
    for attempt in range(6):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'research-security-analysis/1.0'})
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.loads(r.read())
        except Exception as e:
            err = e
            time.sleep(2 * (attempt + 1))
    raise err
def count(filt):
    return get('/works', filter=filt, per_page=1)['meta']['count']
def group(filt, by):
    return get('/works', filter=filt, group_by=by)['group_by']
