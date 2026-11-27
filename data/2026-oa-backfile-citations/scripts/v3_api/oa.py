import os, re, json, sys, time, requests, urllib.parse
# Published copy: the API key (optional; keyless works at low volume) comes from the environment, and every call is
# logged to api_calls.log next to this file.
LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'api_calls.log')
KEY = os.environ.get('OPENALEX_API_KEY')
def get(path, **params):
    url = 'https://api.openalex.org/' + path.lstrip('/')
    p = dict(params); 
    shown = url + ('?' + urllib.parse.urlencode(p) if p else '')
    if KEY: p['api_key'] = KEY
    for i in range(4):
        r = requests.get(url, params=p, timeout=60)
        if r.status_code == 429: time.sleep(2*(i+1)); continue
        break
    with open(LOG, 'a') as f: f.write(f"{time.strftime('%Y-%m-%dT%H:%M:%S')} {r.status_code} GET {shown}\n")
    r.raise_for_status(); return r.json()
