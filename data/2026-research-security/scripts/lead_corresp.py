"""Who leads Canada-China papers, adding the corresponding author. Articles 2015-2025, authors_count
2-50, with CA and CN institutions (API). For first, last and corresponding authors: Canadian only / Chinese only / both /
other (authorship countries). 'Lead' = Canadian if the first, last OR any corresponding author is Canadian (incl. dual).
CA-US baseline: random sample of 4,000 CA-US articles per year. Output ../results/lead_corresp.json"""
import json, collections, concurrent.futures as cf, oa
def cls(a, c):
    cc = set(a.get('countries') or []); return 'both' if 'CA' in cc and c in cc else 'ca' if 'CA' in cc else 'x' if c in cc else 'other'
def summarize(ws, c):
    k = collections.Counter()
    for w in ws:
        au = w.get('authorships') or []
        if len(au) < 2: continue
        k['n'] += 1
        cor = [a for a in au if a.get('is_corresponding')]
        k['has_corr'] += bool(cor)
        f, l = cls(au[0], c), cls(au[-1], c)
        cc = {cls(a, c) for a in cor}
        k['first_' + f] += 1; k['last_' + l] += 1
        if cor:
            k['corr_ca_any'] += bool(cc & {'ca', 'both'}); k['corr_x_only'] += cc <= {'x'}
        k['ca_lead_fl'] += bool({f, l} & {'ca', 'both'})
        k['ca_lead_flc'] += bool(({f, l} | cc) & {'ca', 'both'})
    return dict(k)
def pull(c, y, sample=None):
    f = f'type:article,institutions.country_code:CA,institutions.country_code:{c},publication_year:{y},authors_count:>1,authors_count:<51'
    ws = []
    if sample:
        for p in range(1, sample // 200 + 1):
            ws += oa.get('/works', filter=f, sample=sample, seed=7, per_page=200, page=p, select='id,authorships')['results']
    else:
        cur = '*'
        while cur:
            r = oa.get('/works', filter=f, per_page=200, cursor=cur, select='id,authorships')
            ws += r['results']; cur = r['meta'].get('next_cursor') if r['results'] else None
    return c, y, ws
jobs = [('CN', y, None) for y in range(2015, 2026)] + [('US', y, 4000) for y in range(2015, 2026)]
out = {}; ids = {}
with cf.ThreadPoolExecutor(4) as ex:
    for c, y, ws in ex.map(lambda j: pull(*j), jobs):
        out.setdefault(c, {})[y] = summarize(ws, c)
        if c == 'CN': ids[y] = ws
# verified NRO subset
import csv
VER = {r['work_id'] for r in csv.DictReader(open('../results/nro_verification_verdicts.csv')) if r['verdict'] == 'verified'}
out['NRO'] = {y: summarize([w for w in ws if w['id'].rsplit('/', 1)[-1] in VER], 'CN') for y, ws in ids.items()}
json.dump(out, open('../results/lead_corresp.json', 'w'), indent=1)
P = lambda d, k: 100 * d.get(k, 0) / max(1, d['n'])
for g in ('CN', 'NRO', 'US'):
    print('==', g, 'year n  %with-corr  corr:CA-any  corr:X-only  CAlead(first/last)  CAlead(first/last/corr)')
    for y in sorted(out[g]):
        d = out[g][y]; hc = max(1, d['has_corr'])
        print(y, d['n'], f"{P(d,'has_corr'):4.0f} {100*d.get('corr_ca_any',0)/hc:5.0f} {100*d.get('corr_x_only',0)/hc:5.0f}   {P(d,'ca_lead_fl'):5.0f}  {P(d,'ca_lead_flc'):5.0f}")
