"""Read-only OpenAlex API helper for the 20 Nov 2026 re-check. GET only. Key read from the OPENALEX_API_KEY environment variable, never printed.
No mailto, no email sent anywhere."""
import os, re, time, json, requests
KEY = os.environ.get('OPENALEX_API_KEY')
BASE = 'https://api.openalex.org'
S = requests.Session()
S.headers['User-Agent'] = 'research-security-checks/1.0'

class APIError(Exception):
    pass

def get(path, **params):
    p = dict(params)
    if KEY:
        p['api_key'] = KEY
    err = None
    for attempt in range(6):
        try:
            r = S.get(BASE + path, params=p, timeout=120)
            if r.status_code == 200:
                return r.json()
            if r.status_code in (400, 403, 404):
                # deterministic error: report message without the key
                raise APIError(f'{r.status_code}: {r.text[:400]}')
            err = APIError(f'{r.status_code}: {r.text[:200]}')
        except APIError:
            raise
        except Exception as e:
            err = e
        time.sleep(2 * (attempt + 1))
    raise err

def count(filt, **kw):
    return get('/works', filter=filt, per_page=1, **kw)['meta']['count']

def group(filt, by, **kw):
    return {x['key'].rsplit('/', 1)[-1] if isinstance(x['key'], str) else x['key']: x['count']
            for x in get('/works', filter=filt, group_by=by, **kw)['group_by']}

def dump(obj, name):
    here = os.path.dirname(os.path.abspath(__file__))
    json.dump(obj, open(os.path.join(here, name), 'w'), indent=1, ensure_ascii=False)
