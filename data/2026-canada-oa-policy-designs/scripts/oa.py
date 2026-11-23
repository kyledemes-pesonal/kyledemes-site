"""Shared helpers for the scripts in this folder.

OpenAlex API (https://docs.openalex.org). An API key is optional: set OPENALEX_API_KEY in your environment to use one.
Standard library only. Every script reads and writes files in ../results, relative to this file.
"""
import csv, json, os, time, urllib.error, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                       # this data folder
RESULTS = os.path.join(ROOT, 'results')
# The earlier field note's folder, next to this one: its country table and its list of Canadian repositories.
MONITOR = os.path.join(ROOT, '..', '2026-where-canadas-open-research-lives', 'results')
KEY = os.environ.get('OPENALEX_API_KEY')

# The 12 OpenAlex funder records for the three agencies (CIHR, NSERC, SSHRC, their programs, Canada Research Chairs,
# CERC, CFREF), as in the open access monitor.
TRI = ("F4320334506|F4320321563|F3340254956|F8543264415|F4320324195|F4320334593|F4320321487|"
       "F4320334617|F7697234222|F4320320994|F4320321481|F4320326644")
AG = {'cihr': "F4320334506|F4320321563|F3340254956|F8543264415|F4320324195",
      'nserc': "F4320334593|F4320321487", 'sshrc': "F4320334617|F7697234222"}
BASE = 'type:article|review'


def get(path, **params):
    if KEY:
        params['api_key'] = KEY
    url = 'https://api.openalex.org/' + path + '?' + urllib.parse.urlencode(params, safe=':,|!<>')
    req = urllib.request.Request(url, headers={'User-Agent': 'field-notes-replication/1.0'})
    err = None
    for i in range(5):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except Exception as e:
            err = e
            time.sleep(2 * (i + 1))
    raise err


def count(filt):
    return get('works', filter=filt, per_page=1)['meta']['count']


def by_year(filt):
    return {int(g['key']): g['count'] for g in get('works', filter=filt, group_by='publication_year')['group_by']}


def by_year_route(filt):
    out = {}
    for g in get('works', filter=filt, group_by='publication_year,oa_status')['group_by']:
        d = {s['key']: s['count'] for s in g['groups']}
        d['n'] = g['count']
        out[int(g['key'])] = d
    return out


def carepo_ids():
    """OpenAlex source IDs of the Canadian repositories listed with the open access monitor."""
    p = os.path.join(MONITOR, 'canadian_repositories.csv')
    return [r['id'].rsplit('/', 1)[-1] for r in csv.DictReader(open(p, encoding='utf-8'))]


def carepo_filter():
    return 'locations.source.id:' + '|'.join(carepo_ids())


def load(name):
    return json.load(open(os.path.join(RESULTS, name), encoding='utf-8'))


def save(name, obj):
    with open(os.path.join(RESULTS, name), 'w', encoding='utf-8') as f:
        json.dump(obj, f, indent=1)
