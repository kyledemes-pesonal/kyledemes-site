"""How much of Canada's output would a UK-style rule reach ("only deposited papers count when you apply")?

Proxy: a paper is reached if at least one of its Canadian authors is a regular tri-agency applicant, meaning they have
at least 1, 3 or 5 tri-agency-funded Canadian papers from 2019 to 2025. Random sample of 600 Canadian papers from 2024
(seed 31). Author IDs are used only inside the queries; the output holds aggregate shares only.

Run from the data folder:  python3 checks/applicant_share.py   ->  checks/applicant_share.json   (about 600 requests)
"""
import json, math, os, sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from oa import get, TRI

HERE = os.path.dirname(os.path.abspath(__file__))
ws = []
for page in (1, 2, 3):
    r = get('works', filter='type:article|review,publication_year:2024,institutions.country_code:CA', sample=600, seed=31,
            per_page=200, page=page, select='id,authorships,open_access')
    ws += r['results']


def ca_authors(w):
    out = []
    for a in w['authorships']:
        cc = set(a.get('countries') or []) | {i.get('country_code') for i in a.get('institutions') or []}
        if 'CA' in cc and a.get('author', {}).get('id'):
            out.append((a['author']['id'].rsplit('/', 1)[-1], a.get('author_position'), bool(a.get('is_corresponding'))))
    return out[:100]


def check(w):
    au = ca_authors(w)
    if not au:
        return None
    f = (f"authorships.author.id:{'|'.join(a[0] for a in au)},funders.id:{TRI},publication_year:2019-2025,"
         "institutions.country_code:CA")
    cnt = {x['key'].rsplit('/', 1)[-1]: x['count'] for x in get('works', filter=f, group_by='authorships.author.id')['group_by']}
    # keep only position, corresponding flag and the count for each Canadian author
    return {'closed': w['open_access']['oa_status'] == 'closed',
            'authors': [(pos, corr, cnt.get(i, 0)) for i, pos, corr in au]}


with ThreadPoolExecutor(4) as ex:
    rows = [x for x in ex.map(check, ws) if x]


def share(k, n):
    p = k / n
    return {'k': k, 'n': n, 'pct': round(100 * p, 1), 'ci95_pts': round(196 * math.sqrt(p * (1 - p) / n), 1)}


n = len(rows); nc = sum(r['closed'] for r in rows)
out = {'sampled': len(ws), 'with_canadian_author_id': n}
for thr in (1, 3, 5):
    hit = lambda r: any(c >= thr for *_, c in r['authors'])
    out[f'at_least_{thr}'] = {
        'any_canadian_author': share(sum(hit(r) for r in rows), n),
        'closed_papers_only': share(sum(hit(r) for r in rows if r['closed']), nc),
        'first_last_or_corresponding': share(sum(any(c >= thr and (p in ('first', 'last') or k) for p, k, c in r['authors'])
                                                 for r in rows), n)}
    print(thr, out[f'at_least_{thr}'])
with open(os.path.join(HERE, 'applicant_share.json'), 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=1)
