"""Canada-China collaboration by province, v2: fixes the federal-lab bug in provinces.py and adds a full-text-only version.

The bug in provinces.py: a work counted for the province of EVERY institution ID in a Canadian authorship's lineage, so a
federal lab anywhere in Canada (e.g. an Agriculture and Agri-Food Canada research centre in Alberta) also counted for Ontario
through its Ottawa-based parent department.

Province rule (v2), per Canadian authorship (an authorship with CA among its countries) in the local download:
 1. The authorship's own institutions = the IDs in its stored lineage set that are not an ancestor of another ID in that set
    (ancestry from each institution's OpenAlex `lineage`).
 2. Province = the own institution's geo.region (OpenAlex institution record), if it is a Canadian institution with a region.
 3. If the own institution has no region, use its nearest ancestor (deepest lineage first) that has a region and is not
    federal. Federal = the record's lineage includes a Government of Canada record, or it is a government-type institution
    whose descendants in the download sit in more than one province (a department-level umbrella).
 4. Sensitivity "strict": an own institution that is itself a federal umbrella (department-level record, multi-province)
    gives no province (its geo.region is just its headquarters).
A work counts once for each province any of its Canadian authorships is assigned to.

Full text: the IDs of type:article,institutions.country_code:CA,authors_count:<51,has_fulltext:true for 2018-2020 and
2023-2025 (select=id, cursor paging per half-year, 4 streams at a time), cached as
results/funded_fulltext_cache/ft_ids/<period>.txt.gz; the local download (results/ca_works, built by pull_ca_works.py) is filtered to them.
Funded = the work's stored funders include NSERC, CIHR, SSHRC, CFI (author_panel.FUND: the 5 IDs plus F7697234222, which now
redirects to SSHRC's F4320334617; harmless). NRO = verified Chinese named-research-organization work (VERIFIED=1 set).
Output: results/provinces_v2.json
"""
import os, sys, json, gzip, time, collections, concurrent.futures as cf
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(HERE)
os.environ['VERIFIED'] = '1'
sys.argv = sys.argv[:1]
import author_panel as ap
from funded_fulltext import api

D = os.path.join(HERE, '..', 'results')
CACHE = os.path.join(D, 'funded_fulltext_cache')
IDS = os.path.join(CACHE, 'ft_ids')
YEARS = [2018, 2019, 2020, 2023, 2024, 2025]
S = lambda u: u.rsplit('/', 1)[-1] if u else None

# ---------------------------------------------------------------- full-text IDs
def pull_ft_ids():
    os.makedirs(IDS, exist_ok=True)
    periods = []
    for y in YEARS:
        periods += [(f'{y}a', f'from_publication_date:{y}-01-01,to_publication_date:{y}-06-30'),
                    (f'{y}b', f'from_publication_date:{y}-07-01,to_publication_date:{y}-12-31')]
    def run(p):
        name, f = p; path = f'{IDS}/{name}.txt.gz'; done = f'{IDS}/{name}.done'
        if os.path.exists(done): return name, open(done).read()
        import funded_fulltext as ff, urllib.parse, urllib.request
        if ff.KEY is None: ff.KEY = ff._key()
        cur, n = '*', 0
        with gzip.open(path, 'wt') as fh:
            while cur:
                q = urllib.parse.urlencode({'filter': 'type:article,institutions.country_code:CA,authors_count:<51,has_fulltext:true,' + f,
                                            'select': 'id', 'per_page': 200, 'cursor': cur, 'api_key': ff.KEY})
                for attempt in range(6):
                    try:
                        with urllib.request.urlopen(urllib.request.Request('https://api.openalex.org/works?' + q,
                                                    headers={'User-Agent': 'kyle-funded-fulltext/1.0'}), timeout=120) as r:
                            resp = json.loads(r.read()); break
                    except Exception as e:
                        err = e; time.sleep(2 * (attempt + 1))
                else: raise err
                for w in resp['results']: fh.write(S(w['id']) + '\n'); n += 1
                cur = resp['meta'].get('next_cursor') if resp['results'] else None
        open(done, 'w').write(str(n))
        return name, n
    with cf.ThreadPoolExecutor(4) as ex:
        for name, n in ex.map(run, periods): print(time.strftime('%H:%M:%S'), 'ft ids', name, n, file=sys.stderr, flush=True)
    ft = set()
    for fn in os.listdir(IDS):
        if fn.endswith('.txt.gz'):
            with gzip.open(f'{IDS}/{fn}', 'rt') as fh: ft |= {l.strip() for l in fh if l.strip()}
    return ft

# ---------------------------------------------------------------- institution records
def institutions(ids):
    path = os.path.join(CACHE, 'ca_institutions.json')
    rec = json.load(open(path)) if os.path.exists(path) else {}
    todo = sorted(set(ids) - set(rec))
    chunks = [todo[i:i + 100] for i in range(0, len(todo), 100)]
    def get(ch):
        r = api('/institutions', filter='openalex:' + '|'.join(ch), per_page=100, select='id,display_name,country_code,type,geo,lineage')
        return ch, r['results']
    with cf.ThreadPoolExecutor(4) as ex:
        for ch, res in ex.map(get, chunks):
            got = {S(x['id']): {'n': x.get('display_name'), 'cc': x.get('country_code'), 't': x.get('type'),
                                'r': (x.get('geo') or {}).get('region'), 'lin': [S(l) for l in x.get('lineage') or []]} for x in res}
            for j in ch: rec[j] = got.get(j)
    json.dump(rec, open(path, 'w'))
    return rec

def main():
    ft = pull_ft_ids()
    print('full-text ids', len(ft), file=sys.stderr)
    ids = set()
    for w in ap.works(set(YEARS)):
        for a in w['a']:
            if 'CA' in a[3]: ids |= set(a[2])
    rec = institutions(ids)
    lin = {k: set(v['lin']) if v else {k} for k, v in rec.items()}
    # Government of Canada records (by name) and department-level umbrellas (government type, descendants in >1 province)
    gov_root = {k for k, v in rec.items() if v and v['cc'] == 'CA' and (v['n'] or '').lower() in ('government of canada', 'gouvernement du canada')}
    desc_regions = collections.defaultdict(set)
    for k, v in rec.items():
        if v and v['cc'] == 'CA' and v['r']:
            for anc in lin[k] - {k}: desc_regions[anc].add(v['r'])
    umbrella = {k for k, v in rec.items() if v and v['cc'] == 'CA' and v['t'] == 'government' and len(desc_regions[k] | ({v['r']} if v['r'] else set())) > 1}
    federal = {k for k, v in rec.items() if v and v['cc'] == 'CA' and (lin[k] & gov_root)} | umbrella | gov_root
    print('gov roots', [(k, rec[k]['n']) for k in gov_root], 'umbrellas', len(umbrella), 'federal', len(federal), file=sys.stderr)
    def depth(k): return len(lin.get(k, {k}))
    cache_leaf = {}
    def provs_for(L, strict):
        key = (frozenset(L), strict)
        if key in cache_leaf: return cache_leaf[key]
        leaves = [x for x in L if not any(x in lin.get(y, {y}) for y in L if y != x)]
        out = set()
        for x in leaves:
            v = rec.get(x)
            if not v or v['cc'] != 'CA': continue
            if v['r'] and not (strict and x in umbrella):
                out.add(v['r']); continue
            if v['r'] and strict and x in umbrella: continue
            for anc in sorted(lin[x] - {x}, key=depth, reverse=True):
                a = rec.get(anc)
                if a and a['cc'] == 'CA' and a['r'] and anc not in federal:
                    out.add(a['r']); break
        cache_leaf[key] = out
        return out
    def old_provs(L):  # provinces.py rule: every lineage ID's region
        return {(rec.get(l) or {}).get('r') for l in L if (rec.get(l) or {}).get('cc') == 'CA'} - {None}
    res = {m: {v: collections.defaultdict(lambda: collections.defaultdict(collections.Counter)) for v in ('ft', 'all')} for m in ('v2', 'strict', 'old')}
    seen, n_ft_found, unassigned = set(), 0, collections.Counter()
    for w in ap.works(set(YEARS)):
        if w['w'] in seen or w['y'] not in YEARS: continue
        seen.add(w['w'])
        is_ft = w['w'] in ft; n_ft_found += is_ft
        fu = 'f' if set(w['f']) & ap.FUND else 'o'
        cn = any('CN' in a[3] for a in w['a']); nro = w['w'] in ap.VER_CN
        ca_auth = [frozenset(a[2]) for a in w['a'] if 'CA' in a[3]]
        P = {'v2': set().union(*[provs_for(L, False) for L in ca_auth]) if ca_auth else set(),
             'strict': set().union(*[provs_for(L, True) for L in ca_auth]) if ca_auth else set(),
             'old': set().union(*[old_provs(L) for L in ca_auth]) if ca_auth else set()}
        if not P['v2']: unassigned['v2'] += 1
        if not P['old']: unassigned['old'] += 1
        for m, provs in P.items():
            for v in (('ft', 'all') if is_ft else ('all',)):
                for p in provs:
                    c = res[m][v][p][w['y']]; c['n_' + fu] += 1; c['cn_' + fu] += cn; c['nro_' + fu] += nro
    print('works', len(seen), 'with full text', n_ft_found, 'of', len(ft), 'ft ids; unassigned', dict(unassigned), file=sys.stderr)
    out = {'built': time.strftime('%Y-%m-%d %H:%M'), 'rule': __doc__.split('Province rule (v2)')[1].split('Full text:')[0].strip(),
           'n_works': len(seen), 'n_ft_ids': len(ft), 'n_works_with_ft': n_ft_found, 'unassigned_works': dict(unassigned),
           'federal_ids': sorted(federal), 'umbrella_ids': {k: rec[k]['n'] for k in sorted(umbrella)},
           'counts': {m: {v: {p: {str(y): dict(c) for y, c in sorted(d.items())} for p, d in r.items()} for v, r in rv.items()} for m, rv in res.items()},
           'summary': {}}
    pre, post = (2018, 2019, 2020), (2023, 2024, 2025)
    def sh(d, ys, k): n = sum(d[y]['n_' + k] for y in ys); return (100 * sum(d[y]['cn_' + k] for y in ys) / n) if n else None
    for m in res:
        for v in ('ft', 'all'):
            rows = []
            for p, d in sorted(res[m][v].items(), key=lambda kv: -sum(c['n_f'] + c['n_o'] for c in kv[1].values())):
                n_pre = sum(d[y]['n_f'] + d[y]['n_o'] for y in pre)
                if n_pre < 300: continue
                fpre, fpost, opre, opost = sh(d, pre, 'f'), sh(d, post, 'f'), sh(d, pre, 'o'), sh(d, post, 'o')
                rows.append({'prov': p, 'n_1820': n_pre, 'funded_n_1820': sum(d[y]['n_f'] for y in pre), 'funded_n_2325': sum(d[y]['n_f'] for y in post),
                             'cn_funded_1820': round(fpre, 1), 'cn_funded_2325': round(fpost, 1), 'cn_other_1820': round(opre, 1), 'cn_other_2325': round(opost, 1),
                             'ratio_change': round(100 * ((fpost / opost) / (fpre / opre) - 1), 1) if fpre and opre and opost else None,
                             'nro_funded': [sum(d[y]['nro_f'] for y in pre), sum(d[y]['nro_f'] for y in post)]})
            out['summary'][f'{m}_{v}'] = rows
    json.dump(out, open(os.path.join(D, 'provinces_v2.json'), 'w'), indent=1)
    for k, rows in out['summary'].items():
        print(k)
        for r in rows:
            print(f"  {r['prov'][:22]:22} n18-20 {r['n_1820']:7d}  funded {r['cn_funded_1820']:5.1f}->{r['cn_funded_2325']:5.1f}  other {r['cn_other_1820']:5.1f}->{r['cn_other_2325']:5.1f}  ratio {r['ratio_change']}  NRO funded {r['nro_funded']}")

if __name__ == '__main__':
    main()
