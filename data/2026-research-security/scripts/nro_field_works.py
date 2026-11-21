"""Listed Chinese organizations (NROs) vs big unlisted Chinese institutions (controls), counted as WORKS, by field class,
normalised by each group's own output, for the 24 focal countries of did_wide.py, 2015-2025 (rebuild of
an earlier link-based version, 20 Nov 2026).

Unit: OpenAlex works, type:article, publication_year 2015-2025, co-authored by focal country f and CN
(institutions.country_code:f, institutions.country_code:CN). A work is in the NRO group if any authorship lineage
contains any NRO ID (114 IDs: high/medium CN rows of nro_map.csv plus their listed child_ids), in the control group if
any lineage contains any control ID (247 IDs: CN rows of nro_controls.csv minus the CAS/USTC/MIIT umbrellas and rows
with has_nro_below). A work can be in both groups.
Field class from primary_topic: sens = 35 STRAC-mapped subfields; nons = 16 non-sensitive fields; nons_core = nons
minus 27 Medicine, 28 Neuroscience, 30 Pharmacology. Other works (and works with no primary topic) are 'neither'.
Union counts: OR filters take <=100 values, so each group's union is counted by inclusion-exclusion over batches of
<=100 IDs (repeating the authorships.institutions.lineage filter key ANDs batches), each term with
group_by=primary_topic.subfield.id (cursor-paged). IDs whose institution lineage already contains another ID of the same
set are dropped first (lineage includes ancestors, so the parent catches them): NRO 114 -> 66 IDs (one call),
controls 247 -> 239 (3 batches, 7 calls). Validated for Canada 2018-20 and 2024-25 against a second method: pull every
work ID (select=id,primary_topic, cursor paging) with the FULL unpruned lists in batches of 100 and dedupe locally.
Own output: Own_G[class, t] = all type:article works worldwide with a group-G ID in lineage, same method.
Index[f, class, t] = (W_NRO / W_CTL) / (Own_NRO / Own_CTL). Change 2018-20 -> 2024-25 uses pooled counts per period.
Canada's 95% interval: work-level bootstrap (multinomial over NRO-only / control-only / both works within each period;
own output Poisson). Inference: Canada's rank among the 24 (one-sided permutation p = rank/24).
Links (the old unit, for comparison): sum over IDs of works per lineage ID from group_by=authorships.institutions.lineage,
same ID sets and class filters (the earlier link-based version).
Raw API responses cached under ../results/nro_field_works_cache/ (re-runs are offline). API key read from
the OPENALEX_API_KEY environment variable via oa.py, passed as api_key, never printed; no mailto.
Outputs: ../results/nro_field_works.json, ../results/chart_nro_sensitive_works.json
Usage: python nro_field_works.py [--no-links] [--countries CA,NL,...]
"""
import argparse, csv, datetime, hashlib, json, math, os, random, sys, threading, time
import urllib.error, urllib.parse, urllib.request
import concurrent.futures as cf
from itertools import combinations
from statistics import median

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import oa  # noqa: E402  (loads the API key from the OPENALEX_API_KEY environment variable; never printed)

D = os.path.join(HERE, '..', 'results') + os.sep
CACHE = D + 'nro_field_works_cache' + os.sep
SENS = [1702, 1705, 1707, 1708, 1709, 1711, 1712, 1710, 1703, 2202, 2207, 2208, 2209, 2210, 2212, 2203, 2102, 2103,
        2104, 2105, 2501, 2502, 2503, 2504, 2505, 2506, 2507, 2508, 3104, 3105, 3107, 3108, 1305, 2204, 2402]
NONS = [27, 29, 35, 36, 33, 12, 32, 20, 14, 23, 11, 19, 28, 30, 34, 18]
MED = [27, 28, 30]
NONS_CORE = [x for x in NONS if x not in MED]
CLASSES = ('sens', 'nons', 'nons_core')
YEARS = list(range(2015, 2026))
PRE, POST = (2018, 2019, 2020), (2024, 2025)
OLD8 = ['CA', 'NL', 'GB', 'US', 'FR', 'DE', 'AU', 'JP']
LIN = 'authorships.institutions.lineage'
WORKERS = 4  # <= 4 concurrent requests
_lock = threading.Lock()
FETCHED = []  # (utc timestamp) of every cache entry used


# ---------------------------------------------------------------- API with cache
def api(path, **params):
    key = json.dumps([path, sorted(params.items())])
    fn = CACHE + hashlib.sha1(key.encode()).hexdigest() + '.json'
    if os.path.exists(fn):
        rec = json.load(open(fn))
        with _lock:
            FETCHED.append(rec['fetched'])
        return rec['resp']
    p = dict(params)
    if oa.KEY:
        p['api_key'] = oa.KEY
    url = oa.BASE + path + '?' + urllib.parse.urlencode(p)
    last = None
    for attempt in range(8):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'nro-field-works/1.0'})
            with urllib.request.urlopen(req, timeout=180) as r:
                raw = json.loads(r.read())
            break
        except urllib.error.HTTPError as e:  # str(e) has code + reason, not the URL
            last = f'HTTP {e.code} {e.reason}'
            if e.code in (400, 403, 404):
                raise RuntimeError(f'{path} {params.get("filter", "")[:120]}...: {last}')
        except Exception as e:
            last = type(e).__name__
        time.sleep(min(60, 2 ** attempt))
    else:
        raise RuntimeError(f'{path}: gave up after retries ({last})')
    meta = raw.get('meta', {})
    resp = {'meta': {'count': meta.get('count'), 'next_cursor': meta.get('next_cursor')}}
    if 'group_by' in raw and raw['group_by']:
        resp['group_by'] = [{'key': g['key'], 'count': g['count']} for g in raw['group_by']]
    elif 'group_by' in raw:
        resp['group_by'] = []
    if 'results' in raw:
        resp['results'] = [{'id': w['id'], 'sub': ((w.get('primary_topic') or {}).get('subfield') or {}).get('id'),
                            'lineage': w.get('lineage')} for w in raw['results']]
    now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
    tmp = fn + f'.tmp{threading.get_ident()}'
    json.dump({'fetched': now, 'query': key, 'resp': resp}, open(tmp, 'w'))
    os.replace(tmp, fn)
    with _lock:
        FETCHED.append(now)
    return resp


def grouped(filt, by='primary_topic.subfield.id'):
    """(total works, {group key tail: count}) for a filter, all groups via cursor paging."""
    out, cur, total = {}, '*', None
    while cur:
        r = api('/works', filter=filt, group_by=by, per_page=200, cursor=cur)
        if total is None:
            total = r['meta']['count']
        for g in r['group_by']:
            k = str(g['key']).rsplit('/', 1)[-1]
            out[k] = out.get(k, 0) + g['count']
        cur = r['meta'].get('next_cursor') if r['group_by'] else None
    return total, out


def classify(total, sub):
    """Subfield counts -> class counts. Keys that are not subfield numbers (e.g. 'unknown') fall in 'neither'."""
    c = {'sens': 0, 'nons': 0, 'nons_core': 0}
    for k, n in sub.items():
        if not k.isdigit():
            continue
        s = int(k)
        if s in SENS:
            c['sens'] += n
        if s // 100 in NONS:
            c['nons'] += n
        if s // 100 in NONS_CORE:
            c['nons_core'] += n
    c['total'] = total
    c['neither'] = total - c['sens'] - c['nons']
    return c


# ---------------------------------------------------------------- ID sets
def load_sets():
    nro = [r for r in csv.DictReader(open(D + 'nro_map.csv')) if r['confidence'] in ('high', 'medium') and r['country'] == 'CN']
    N = set()
    for r in nro:
        N.add(r['openalex_id'])
        N |= {c.strip() for c in r['child_ids'].replace('|', ';').split(';') if c.strip()}
    umb = {'Chinese Academy of Sciences', 'Ministry of Industry and Information Technology', 'University of Science and Technology of China'}
    C = {r['id'] for r in csv.DictReader(open(D + 'nro_controls.csv'))
         if r['country'] == 'CN' and r['display_name'] not in umb and r['has_nro_below'] in ('', 'False', 'false', '0')}
    return len(nro), sorted(N), sorted(C)


def lineages(ids):
    out = {}
    for i in range(0, len(ids), 100):
        r = api('/institutions', filter='openalex:' + '|'.join(ids[i:i + 100]), select='id,lineage', per_page=100)
        for x in r['results']:
            out[x['id'].rsplit('/', 1)[-1]] = [a.rsplit('/', 1)[-1] for a in (x['lineage'] or [])]
    return out


def prune(ids):
    """Drop IDs whose lineage contains another ID of the same set (the ancestor's lineage filter already catches them)."""
    L = lineages(ids)
    S = set(ids)
    missing = S - set(L)
    if missing:
        raise RuntimeError(f'institutions not found: {sorted(missing)}')
    return sorted(i for i in ids if not any(a in S and a != i for a in L[i]))


def batches(ids, k=100):
    return [ids[i:i + k] for i in range(0, len(ids), k)]


# ---------------------------------------------------------------- counting
def base_filter(scope, y):
    if scope == 'WORLD':
        return f'type:article,publication_year:{y}'
    return f'type:article,institutions.country_code:{scope},institutions.country_code:CN,publication_year:{y}'


def union_by_class(base, ids):
    """Inclusion-exclusion over <=100-ID batches; returns class counts for works with any ID in lineage."""
    bs = batches(ids)
    tot, sub = 0, {}
    for k in range(1, len(bs) + 1):
        sign = 1 if k % 2 else -1
        for S in combinations(range(len(bs)), k):
            filt = base + ''.join(f',{LIN}:' + '|'.join(bs[s]) for s in S)
            t, g = grouped(filt)
            tot += sign * t
            for key, n in g.items():
                sub[key] = sub.get(key, 0) + sign * n
    return classify(tot, sub)


def cell(scope, y, Np, Cp):
    base = base_filter(scope, y)
    t, g = grouped(base)
    return scope, y, {'all': classify(t, g), 'nro': union_by_class(base, Np), 'ctl': union_by_class(base, Cp)}


def link_cell(f, cls, y, N, C):
    """Old unit: institution-work links, as the earlier link-based version (sum over IDs of per-lineage-ID work counts)."""
    flt = {'sens': 'primary_topic.subfield.id:' + '|'.join(map(str, SENS)),
           'nons': 'primary_topic.field.id:' + '|'.join(map(str, NONS)),
           'nons_core': 'primary_topic.field.id:' + '|'.join(map(str, NONS_CORE))}[cls]
    _, out = grouped(base_filter(f, y) + ',' + flt, by=LIN)
    return f, cls, y, [sum(out.get(i, 0) for i in N), sum(out.get(i, 0) for i in C)]


def work_ids(base, ids):
    """Second method: every work ID (and primary subfield) with any of ids in lineage, deduped locally."""
    works = {}
    for b in batches(ids):
        cur = '*'
        while cur:
            r = api('/works', filter=base + f',{LIN}:' + '|'.join(b), select='id,primary_topic', per_page=200, cursor=cur)
            for w in r['results']:
                works[w['id']] = w['sub']
            cur = r['meta'].get('next_cursor') if r['results'] else None
    return works


def sub_class(sub):
    if not sub:
        return set()
    s = int(str(sub).rsplit('/', 1)[-1])
    out = set()
    if s in SENS:
        out.add('sens')
    if s // 100 in NONS:
        out.add('nons')
    if s // 100 in NONS_CORE:
        out.add('nons_core')
    return out


# ---------------------------------------------------------------- statistics
def pooled(counts, scope, grp, cls, years):
    return sum(counts[scope][y][grp][cls] for y in years)


def index_ratio(counts, f, cls, years, norm=True):
    r = pooled(counts, f, 'nro', cls, years) / pooled(counts, f, 'ctl', cls, years)
    if norm:
        r /= pooled(counts, 'WORLD', 'nro', cls, years) / pooled(counts, 'WORLD', 'ctl', cls, years)
    return r


def multinomial3(rng, n, p):
    a = rng.binomialvariate(n, p[0])
    b = rng.binomialvariate(n - a, p[1] / (1 - p[0])) if p[0] < 1 else 0
    return a, b, n - a - b


def poisson(rng, lam):  # normal approximation is exact enough for the very large own-output counts
    return max(1, round(rng.gauss(lam, math.sqrt(lam))))


def bootstrap_ca(wl, own, cls_list, B=4000, seed=20261120):
    """wl[period][cls] = (nro_only, ctl_only, both) works for Canada; own[period][cls] = (Own_NRO, Own_CTL)."""
    rng = random.Random(seed)
    draws = {c: [] for c in cls_list}
    for _ in range(B):
        lr = {}
        for c in cls_list:
            val = []
            for P in ('pre', 'post'):
                a, b, ab = wl[P][c]
                n = a + b + ab
                x, y_, z = multinomial3(rng, n, (a / n, b / n, ab / n))
                on, oc = own[P][c]
                val.append(((x + z) / (y_ + z)) / (poisson(rng, on) / poisson(rng, oc)))
            lr[c] = math.log(val[1] / val[0])
            draws[c].append(lr[c])
        for other in ('nons', 'nons_core'):
            if 'sens' in lr and other in lr:
                draws.setdefault('ddd_sens_minus_' + other, []).append(lr['sens'] - lr[other])
    ci = {}
    for k, v in draws.items():
        v.sort()
        ci[k] = [100 * (math.exp(v[int(0.025 * B)]) - 1), 100 * (math.exp(v[int(0.975 * B) - 1]) - 1)]
    return ci


def rank_of(v, f):  # 1 = most negative
    order = sorted(v, key=v.get)
    return order.index(f) + 1, order


def pct(x):
    return 100 * (x - 1)


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--no-links', action='store_true')
    ap.add_argument('--countries', default='')
    a = ap.parse_args()
    os.makedirs(CACHE, exist_ok=True)
    focal_all = sorted(json.load(open(D + 'pairs_wide.json')))
    focal = [x for x in a.countries.split(',') if x] or focal_all
    n_rows, N, C = load_sets()
    Np, Cp = prune(N), prune(C)
    print(f'NRO rows {n_rows}, IDs {len(N)} (pruned {len(Np)}); control IDs {len(C)} (pruned {len(Cp)}); focal {len(focal)}')

    # 1. works counts per scope x year (WORLD = own output)
    scopes = ['WORLD'] + [f for f in OLD8 if f in focal] + [f for f in focal if f not in OLD8]
    counts = {s: {} for s in scopes}
    jobs = [(s, y) for s in scopes for y in YEARS]
    with cf.ThreadPoolExecutor(WORKERS) as ex:
        for i, (s, y, c) in enumerate(ex.map(lambda j: cell(j[0], j[1], Np, Cp), jobs)):
            counts[s][y] = c
            if (i + 1) % 22 == 0:
                print(f'  works cells {i + 1}/{len(jobs)}', flush=True)

    # 2. validation + Canada's work-level data (second method, full unpruned lists)
    wl_years = {}
    validation = {}
    if 'CA' in focal:
        def wjob(y):
            base = base_filter('CA', y)
            return y, work_ids(base, N), work_ids(base, C)
        with cf.ThreadPoolExecutor(WORKERS) as ex:
            for y, wn, wc in ex.map(wjob, PRE + POST):
                wl_years[y] = (wn, wc)
                v = {}
                for grp, ws in (('nro', wn), ('ctl', wc)):
                    dd = {c: 0 for c in CLASSES}
                    for sub in ws.values():
                        for c in sub_class(sub):
                            dd[c] += 1
                    dd['total'] = len(ws)
                    ie = counts['CA'][y][grp]
                    v[grp] = {k: {'dedupe': dd[k], 'incl_excl': ie[k]} for k in ('total',) + CLASSES}
                validation[y] = v
        print('validation (dedupe vs inclusion-exclusion):', json.dumps({y: {g: {k: [x['dedupe'], x['incl_excl']] for k, x in v[g].items()} for g in v} for y, v in validation.items()}))

    # 3. links (old unit)
    links = {}
    if not a.no_links:
        lf = [f for f in OLD8 if f in focal] + [f for f in focal if f not in OLD8]
        ljobs = [(f, c, y) for f in lf for c in CLASSES for y in YEARS]
        with cf.ThreadPoolExecutor(WORKERS) as ex:
            for i, (f, c, y, nc) in enumerate(ex.map(lambda j: link_cell(*j, N, C), ljobs)):
                links.setdefault(f, {}).setdefault(c, {})[y] = nc
                if (i + 1) % 66 == 0:
                    print(f'  link cells {i + 1}/{len(ljobs)}', flush=True)

    # 4. statistics
    F = [f for f in focal if f in counts]
    res = {'change': {}, 'index': {}, 'rank': {}, 'ddd': {}, 'ca_vs_peer_median_by_year': {}, 'own': {}}
    for cls in CLASSES:
        own = {P: [pooled(counts, 'WORLD', g, cls, Y) for g in ('nro', 'ctl')] for P, Y in (('pre', PRE), ('post', POST))}
        own_factor = (own['post'][0] / own['post'][1]) / (own['pre'][0] / own['pre'][1])
        res['own'][cls] = {'pre': own['pre'], 'post': own['post'], 'own_ratio_change_pct': pct(own_factor)}
        ch = {}
        for f in F:
            raw = index_ratio(counts, f, cls, POST, False) / index_ratio(counts, f, cls, PRE, False)
            row = {'works_raw_pct': pct(raw), 'works_norm_pct': pct(raw / own_factor),
                   'nro_pre': pooled(counts, f, 'nro', cls, PRE), 'ctl_pre': pooled(counts, f, 'ctl', cls, PRE),
                   'nro_post': pooled(counts, f, 'nro', cls, POST), 'ctl_post': pooled(counts, f, 'ctl', cls, POST)}
            if f in links:
                q = lambda ys: sum(links[f][cls][y][0] for y in ys) / sum(links[f][cls][y][1] for y in ys)
                row['links_raw_pct'] = pct(q(POST) / q(PRE))
            ch[f] = row
        res['change'][cls] = ch
        base = {f: index_ratio(counts, f, cls, PRE) for f in F}
        res['index'][cls] = {f: {y: 100 * index_ratio(counts, f, cls, (y,)) / base[f] for y in YEARS} for f in F}
        if 'CA' in F and len(F) > 1:  # ranks need peers (a --countries CA run skips them)
            v = {f: ch[f]['works_norm_pct'] for f in F}
            r, order = rank_of(v, 'CA')
            peers = [v[f] for f in F if f != 'CA']
            rk = {'ca_rank': r, 'n': len(F), 'p_one_sided': r / len(F), 'ca_pct': v['CA'], 'peer_median_pct': median(peers),
                  'ca_minus_peer_median_pp': v['CA'] - median(peers), 'order': [[f, round(v[f], 1)] for f in order]}
            if all('links_raw_pct' in ch[f] for f in F):
                vl = {f: ch[f]['links_raw_pct'] for f in F}
                rl, ol = rank_of(vl, 'CA')
                rk['links'] = {'ca_rank': rl, 'ca_pct': vl['CA'], 'peer_median_pct': median([vl[f] for f in F if f != 'CA']),
                               'order': [[f, round(vl[f], 1)] for f in ol]}
            res['rank'][cls] = rk
            idx = res['index'][cls]
            res['ca_vs_peer_median_by_year'][cls] = {y: {'ca': idx['CA'][y], 'peer_median': median(idx[f][y] for f in F if f != 'CA'),
                                                         'ca_over_median_pct': pct(idx['CA'][y] / median(idx[f][y] for f in F if f != 'CA'))}
                                                     for y in YEARS}
    for other in ('nons', 'nons_core'):
        d = {f: 100 * (math.exp(math.log(1 + res['change']['sens'][f]['works_norm_pct'] / 100)
                                - math.log(1 + res['change'][other][f]['works_norm_pct'] / 100)) - 1) for f in F}
        out = {'by_country': d}
        if 'CA' in F and len(F) > 1:
            r, order = rank_of(d, 'CA')
            out.update({'ca_rank': r, 'p_one_sided': r / len(F), 'peer_median_pct': median(d[f] for f in F if f != 'CA'),
                        'order': [[f, round(d[f], 1)] for f in order]})
        res['ddd']['sens_minus_' + other] = out

    # 5. Canada's interval (work-level bootstrap) + Poisson interval for comparison
    if wl_years:
        wl, own = {}, {}
        for P, Y in (('pre', PRE), ('post', POST)):
            wl[P], own[P] = {}, {}
            for cls in CLASSES:
                a_ = b_ = ab = 0
                for y in Y:
                    wn, wc = wl_years[y]
                    for w in set(wn) | set(wc):
                        sub = wn.get(w) if w in wn else wc.get(w)
                        if cls not in sub_class(sub):
                            continue
                        inn, inc = w in wn, w in wc
                        a_ += inn and not inc
                        b_ += inc and not inn
                        ab += inn and inc
                wl[P][cls] = (a_, b_, ab)
                own[P][cls] = tuple(pooled(counts, 'WORLD', g, cls, Y) for g in ('nro', 'ctl'))
        ci = bootstrap_ca(wl, own, CLASSES)
        pois = {}
        for cls in CLASSES:
            r = res['change'][cls]['CA']
            se = math.sqrt(sum(1 / r[k] for k in ('nro_pre', 'ctl_pre', 'nro_post', 'ctl_post')))
            m = math.log(1 + r['works_norm_pct'] / 100)
            pois[cls] = [pct(math.exp(m - 1.96 * se)), pct(math.exp(m + 1.96 * se))]
        res['ca_ci'] = {'bootstrap_95': ci, 'poisson_95_ignoring_overlap': pois,
                        'work_level_counts': {P: {c: dict(zip(('nro_only', 'ctl_only', 'both'), wl[P][c])) for c in CLASSES} for P in wl}}

    # neither-class counts
    neither = {s: {g: {'neither': sum(counts[s][y][g]['neither'] for y in YEARS), 'total': sum(counts[s][y][g]['total'] for y in YEARS)}
                   for g in ('all', 'nro', 'ctl')} for s in counts}
    pulled = sorted(FETCHED)
    out = {'meta': {'script': 'scripts/nro_field_works.py', 'pulled_utc': [pulled[0], pulled[-1]] if pulled else None,
                    'focal': F, 'years': YEARS, 'pre': PRE, 'post': POST, 'nro_rows': n_rows, 'nro_ids': len(N),
                    'nro_ids_pruned': len(Np), 'ctl_ids': len(C), 'ctl_ids_pruned': len(Cp),
                    'classes': {'sens_subfields': SENS, 'nons_fields': NONS, 'nons_core_fields': NONS_CORE},
                    'index': '(W_NRO/W_CTL)/(Own_NRO/Own_CTL); change uses pooled counts per period; pct = 100*(ratio-1)'},
           'counts': counts, 'links': links, 'validation': validation, 'neither': neither, **res}
    json.dump(out, open(D + 'nro_field_works.json', 'w'), indent=1)

    chart = {}
    for cls in ('sens', 'nons', 'nons_core'):
        rows = []
        for y in YEARS:
            row = {'y': y}
            for f in F:
                row[f.lower()] = round(res['index'][cls][f][y], 1)
            if 'CA' in F and len(F) > 1:
                row['peer_median'] = round(median(res['index'][cls][f][y] for f in F if f != 'CA'), 1)
            rows.append(row)
        chart[cls] = rows
    json.dump(chart, open(D + 'chart_nro_sensitive_works.json', 'w'), indent=1)

    # 6. print summary
    print(f'pulled (UTC) {out["meta"]["pulled_utc"]}')
    for cls in CLASSES:
        print(f'== {cls}: own NRO/CTL ratio change {res["own"][cls]["own_ratio_change_pct"]:+.1f}%')
        for f in OLD8:
            if f in res['change'][cls]:
                r = res['change'][cls][f]
                print(f'  {f}: works raw {r["works_raw_pct"]:+.0f}%  norm {r["works_norm_pct"]:+.0f}%  links {r.get("links_raw_pct", float("nan")):+.0f}%')
        if cls in res['rank']:
            rk = res['rank'][cls]
            print(f'  CA rank {rk["ca_rank"]}/{rk["n"]} p={rk["p_one_sided"]:.3f} peer median {rk["peer_median_pct"]:+.1f}% CA-median {rk["ca_minus_peer_median_pp"]:+.1f}pp')
            print('  ', ' '.join(f'{f}:{v:+.0f}' for f, v in rk['order']))
    for k, v in res['ddd'].items():
        print(k, 'CA rank', v.get('ca_rank'), ' '.join(f'{f}:{x:+.0f}' for f, x in v.get('order', [])))
    if 'ca_ci' in res:
        print('CA CI', json.dumps(res['ca_ci']['bootstrap_95']))


if __name__ == '__main__':
    main()
