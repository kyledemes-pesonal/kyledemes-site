"""Funded vs other, rerun on works OpenAlex has full text for (has_fulltext:true), side by side with all works.

Why: where OpenAlex has a work's full text, its funder field catches 93-97% of tri-agency credits; without full text it is
roughly Crossref's deposit (53-66%). Full-text coverage grew faster for non-China Canadian papers than for Canada-China papers,
so on all papers the "funded" China share falls partly for measurement reasons
(a hand-checked recall study of acknowledgement text, not published; see MANIFEST.md). Every number here is computed twice: ft (has_fulltext:true) and all.

Definitions:
- Unit: type:article, counted by publication_year. Co-authorship = institutions.country_code of both countries.
- Canada funded = funders.id in NSERC F4320334593, CIHR F4320334506, SSHRC F4320334617, CFI F4320319952 and F4320320995.
  F7697234222 is left out: it redirects to F4320334617 (checked on the API), so it adds nothing.
- Other = all Canadian articles minus funded (same filters). Share = papers with a partner co-author / papers in the group.
- Funded-to-other ratio = funded share / other share. Changes use POOLED counts over the years of each period.
- Sensitive / non-sensitive = primary_topic.subfield.id (35 subfields mapped to the 11 STRAC areas) / primary_topic.field.id lists below.
- Peers: each country's own main funders (PEER_FUND below, found by name with /funders?search=); US NIH = F4320332161.

Queries (all cached as raw JSON under results/funded_fulltext_cache/, re-run with REFRESH=1 to refetch):
  A. Canada, for class in all/sens/nonsens, funded 0/1, ft 0/1, year 2015-2025:
     /works?filter=type:article,institutions.country_code:CA,publication_year:Y[,class][,funders.id:CA][,has_fulltext:true]
            &group_by=institutions.country_code      (the CA group is the denominator; each partner's group the numerator)
  B. Peers and Canada, for country c, partner none/CN, funded 0/1, ft 0/1:
     /works?filter=type:article,institutions.country_code:c[,institutions.country_code:CN][,funders.id:<c's set>]
            [,has_fulltext:true],publication_year:2015-2025&group_by=publication_year
Outputs: results/funded_fulltext.json (everything), results/chart_funded_fulltext_f1.json (yearly funded/other shares by partner),
  results/chart_funded_fulltext_c4.json (China lines + 19-partner bars), results/chart_funded_fulltext_c5.json (sensitive vs other),
  results/chart_funded_fulltext_peers.json (9-country bars).
"""
import os, sys, json, hashlib, math, random, statistics as st, time, urllib.parse, urllib.request
import concurrent.futures as cf

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
D = os.path.join(HERE, '..', 'results')
CACHE = os.path.join(D, 'funded_fulltext_cache')
REFRESH = os.environ.get('REFRESH') == '1'

YEARS = list(range(2015, 2026))
CA_FUND = 'F4320334593|F4320334506|F4320334617|F4320319952|F4320320995'
SENS = [1702, 1705, 1707, 1708, 1709, 1711, 1712, 1710, 1703, 2202, 2207, 2208, 2209, 2210, 2212, 2203, 2102, 2103, 2104, 2105,
        2501, 2502, 2503, 2504, 2505, 2506, 2507, 2508, 3104, 3105, 3107, 3108, 1305, 2204, 2402]
NONSENS = ['27', '29', '35', '36', '33', '12', '32', '20', '14', '23', '11', '19', '28', '30', '34', '18']
CLS = {'all': '', 'sens': ',primary_topic.subfield.id:' + '|'.join(map(str, SENS)),
       'nonsens': ',primary_topic.field.id:' + '|'.join(NONSENS)}
PARTNERS19 = ['RU', 'TR', 'CN', 'IR', 'KR', 'HK', 'JP', 'ES', 'IN', 'BR', 'DE', 'AU', 'IT', 'GB', 'US', 'NL', 'SE', 'FR', 'CH']
F1_PARTNERS = ['CN', 'IR', 'RU', 'HK', 'US', 'GB', 'DE', 'IN']
C5_COMPS = ['US', 'GB', 'DE', 'FR', 'AU', 'JP', 'IN', 'KR']
CONCERN = {'CN', 'HK', 'IR', 'RU'}
NAMES = {'CN': 'China', 'HK': 'Hong Kong', 'IR': 'Iran', 'RU': 'Russia', 'US': 'United States', 'GB': 'United Kingdom',
         'DE': 'Germany', 'IN': 'India', 'FR': 'France', 'AU': 'Australia', 'JP': 'Japan', 'KR': 'South Korea', 'TR': 'Türkiye',
         'ES': 'Spain', 'BR': 'Brazil', 'IT': 'Italy', 'NL': 'Netherlands', 'SE': 'Sweden', 'CH': 'Switzerland', 'CA': 'Canada'}
PEER_FUND = {'CA': CA_FUND,
             'GB': 'F4320334627|F4320334626|F4320334629|F4320314731|F4320334631',  # UKRI councils (peerfund.py)
             'AU': 'F4320334704|F4320334705',                                     # ARC, NHMRC
             'DE': 'F4320320879', 'JP': 'F4320334764', 'NL': 'F4320321800', 'FR': 'F4320320883',  # DFG, JSPS, NWO, ANR
             'US': 'F4320306076|F4320332161',                                     # NSF, NIH
             'CH': 'F4320320924'}                                                 # SNSF
FT = ',has_fulltext:true'

# ---------------------------------------------------------------- API with a raw-response cache
def _key():
    import oa  # reads OPENALEX_API_KEY from the OPENALEX_API_KEY environment variable; never printed
    return oa.KEY
KEY = None
def api(path, **params):
    global KEY
    os.makedirs(CACHE, exist_ok=True)
    h = hashlib.sha1((path + '?' + urllib.parse.urlencode(sorted(params.items()))).encode()).hexdigest()[:20]
    fn = os.path.join(CACHE, h + '.json')
    if os.path.exists(fn) and not REFRESH:
        return json.load(open(fn))['response']
    if KEY is None: KEY = _key()
    url = 'https://api.openalex.org' + path + '?' + urllib.parse.urlencode({**params, 'api_key': KEY})
    err = None
    for attempt in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'kyle-funded-fulltext/1.0'}), timeout=120) as r:
                resp = json.loads(r.read())
            json.dump({'path': path, 'params': params, 'fetched': time.strftime('%Y-%m-%d %H:%M:%S'), 'response': resp}, open(fn, 'w'))
            return resp
        except Exception as e:
            err = e; time.sleep(2 * (attempt + 1))
    raise err

def grp(filt, by):
    return {x['key'].rsplit('/', 1)[-1]: x['count'] for x in api('/works', filter=filt, group_by=by)['group_by']}

# ---------------------------------------------------------------- pulls
def pull():
    jobs_a = [(c, fu, ft, y) for c in CLS for fu in (0, 1) for ft in (0, 1) for y in YEARS]
    def ja(j):
        c, fu, ft, y = j
        f = f'type:article,institutions.country_code:CA,publication_year:{y}' + CLS[c] + (f',funders.id:{CA_FUND}' if fu else '') + (FT if ft else '')
        return j, grp(f, 'institutions.country_code')
    jobs_b = [(c, p, fu, ft) for c in PEER_FUND for p in (None, 'CN') for fu in (0, 1) for ft in (0, 1)]
    def jb(j):
        c, p, fu, ft = j
        f = f'type:article,institutions.country_code:{c}' + (f',institutions.country_code:{p}' if p else '') + \
            (f',funders.id:{PEER_FUND[c]}' if fu else '') + (FT if ft else '') + ',publication_year:2015-2025'
        return j, {int(k): v for k, v in grp(f, 'publication_year').items()}
    A, B = {}, {}
    with cf.ThreadPoolExecutor(4) as ex:   # never more than 4 requests at once
        for j, d in ex.map(ja, jobs_a): A[j] = d
        for j, d in ex.map(jb, jobs_b): B[j] = d
    return A, B

# ---------------------------------------------------------------- helpers
def cells(fn, FN, n, N):
    """funded-with-partner, funded-without, other-with, other-without"""
    return fn, FN - fn, n - fn, (N - FN) - (n - fn)
def ratio_from(a, b, c, d):
    return (a / (a + b)) / (c / (c + d))
def pois(lam, rnd):
    if lam > 60: return max(0, int(round(rnd.gauss(lam, math.sqrt(lam)))))
    L, k, p = math.exp(-lam), 0, 1.0
    while True:
        p *= rnd.random()
        if p <= L: return k
        k += 1
def r1(x, n=1): return None if x is None else round(x, n)

def main():
    A, B = pull()
    # Canada tables by class / ft / partner / year: fn, FN, n, N
    def ca(c, ft, p, y):
        fa, aa = A[(c, 1, ft, y)], A[(c, 0, ft, y)]
        return fa.get(p, 0), fa.get('CA', 0), aa.get(p, 0), aa.get('CA', 0)
    def pooled(c, ft, p, ys):
        s = [0, 0, 0, 0]
        for y in ys:
            for i, v in enumerate(ca(c, ft, p, y)): s[i] += v
        return tuple(s)
    def rat(t): fn, FN, n, N = t; return ratio_from(*cells(fn, FN, n, N))
    def shares(t):
        fn, FN, n, N = t; return 100 * fn / FN, 100 * (n - fn) / (N - FN)
    def chg(c, ft, p, pre, post): return 100 * (rat(pooled(c, ft, p, post)) / rat(pooled(c, ft, p, pre)) - 1)
    P1920, P2425, P1516, P1820, P2325, P1718 = (2019, 2020), (2024, 2025), (2015, 2016), (2018, 2019, 2020), (2023, 2024, 2025), (2017, 2018)
    out = {'built': time.strftime('%Y-%m-%d %H:%M'), 'funders_CA': CA_FUND, 'peer_funders': PEER_FUND,
           'note': 'ft = has_fulltext:true; all = every work. Changes from pooled counts. Ratio = funded share / other share.'}
    V = ('ft', 'all')
    # ---- step 1: Canada-China by year
    s1 = {'by_year': {}, 'changes': {}}
    for v in V:
        ft = int(v == 'ft'); rows = []
        for y in YEARS:
            fn, FN, n, N = ca('all', ft, 'CN', y); fs, os_ = shares((fn, FN, n, N))
            rows.append({'y': y, 'funded_N': FN, 'funded_CN': fn, 'other_N': N - FN, 'other_CN': n - fn, 'all_N': N, 'all_CN': n,
                         'funded_share': r1(fs, 2), 'other_share': r1(os_, 2), 'all_share': r1(100 * n / N, 2), 'ratio': round(fs / os_, 3)})
        s1['by_year'][v] = rows
        s1['changes'][v] = {
            'ratio_1920_to_2425': r1(chg('all', ft, 'CN', P1920, P2425)), 'ratio_1820_to_2325': r1(chg('all', ft, 'CN', P1820, P2325)),
            'ratio_2020_to_2025': r1(chg('all', ft, 'CN', (2020,), (2025,))),
            'pooled_ratio_1920': round(rat(pooled('all', ft, 'CN', P1920)), 3), 'pooled_ratio_2425': round(rat(pooled('all', ft, 'CN', P2425)), 3),
            'funded_share_1920_2425': [r1(shares(pooled('all', ft, 'CN', P))[0], 2) for P in (P1920, P2425)],
            'other_share_1920_2425': [r1(shares(pooled('all', ft, 'CN', P))[1], 2) for P in (P1920, P2425)],
            'funded_share_change_2020_2025': r1(100 * (shares(ca('all', ft, 'CN', 2025))[0] / shares(ca('all', ft, 'CN', 2020))[0] - 1)),
        }
    out['step1_canada_china'] = s1
    # ---- step 2: 19 partners
    s2 = []
    for p in PARTNERS19:
        row = {'p': p, 'name': NAMES[p]}
        for v in V:
            ft = int(v == 'ft')
            row[f'after_{v}'] = r1(chg('all', ft, p, P1920, P2425)); row[f'before_{v}'] = r1(chg('all', ft, p, P1516, P1920))
        s2.append(row)
    out['step2_partners19'] = {'rows': s2, 'median_after': {v: r1(st.median(r[f'after_{v}'] for r in s2)) for v in V},
                               'median_before': {v: r1(st.median(r[f'before_{v}'] for r in s2)) for v in V},
                               'median_after_15_comparators': {v: r1(st.median(r[f'after_{v}'] for r in s2 if r['p'] not in CONCERN)) for v in V}}
    # ---- step 3: peers, CN, pooled; bootstrap
    def pc(c, ft, ys):
        g = lambda p, fu: B[(c, p, fu, ft)]
        return tuple(sum(x.get(y, 0) for y in ys) for x in (g('CN', 1), g(None, 1), g('CN', 0), g(None, 0)))
    s3 = {}
    rnd = random.Random(20261120); NB = 10000
    for v in V:
        ft = int(v == 'ft'); res = {}
        for base_name, base in (('2015-16', P1516), ('2017-18', P1718), ('2019-20', P1920)):
            ch = {c: 100 * (rat(pc(c, ft, P2425)) / rat(pc(c, ft, base)) - 1) for c in PEER_FUND}
            peers = [ch[c] for c in PEER_FUND if c != 'CA']; med = st.median(peers)
            rank = 1 + sum(1 for c in PEER_FUND if ch[c] < ch['CA'])
            res[base_name] = {'change': {c: r1(x) for c, x in sorted(ch.items(), key=lambda kv: kv[1])}, 'canada_rank_of_9': rank,
                              'peer_median': r1(med), 'canada_minus_median_pts': r1(ch['CA'] - med),
                              'canada_vs_median_relative': r1(100 * ((1 + ch['CA'] / 100) / (1 + med / 100) - 1))}
        # bootstrap on base 2019-20: Poisson on the 8 cells per country
        base_cells = {c: (cells(*pc(c, ft, P1920)), cells(*pc(c, ft, P2425))) for c in PEER_FUND}
        draws_ca, draws_gap, draws_rel, below = [], [], [], 0
        for _ in range(NB):
            chs = {}
            for c, (pre, post) in base_cells.items():
                a = [pois(x, rnd) for x in pre]; b = [pois(x, rnd) for x in post]
                chs[c] = 100 * (ratio_from(*b) / ratio_from(*a) - 1)
            med = st.median(chs[c] for c in chs if c != 'CA')
            draws_ca.append(chs['CA']); draws_gap.append(chs['CA'] - med); draws_rel.append(100 * ((1 + chs['CA'] / 100) / (1 + med / 100) - 1))
            below += chs['CA'] < med
        q = lambda L: [r1(sorted(L)[int(0.025 * NB)]), r1(sorted(L)[int(0.975 * NB) - 1])]
        res['ci95_2019-20'] = {'canada_change': q(draws_ca), 'canada_minus_median_pts': q(draws_gap), 'canada_vs_median_relative': q(draws_rel),
                               'share_of_draws_canada_below_median': round(below / NB, 3),
                               'method': 'parametric Poisson bootstrap (10,000) on the 4 cells (funded/other x CN/not) per period per country'}
        res['counts_2019-20_2024-25'] = {c: {'pre': pc(c, ft, P1920), 'post': pc(c, ft, P2425)} for c in PEER_FUND}
        s3[v] = res
    out['step3_peers_cn'] = s3
    # ---- step 4: sensitive vs non-sensitive
    s4 = {}
    for v in V:
        ft = int(v == 'ft'); s4[v] = {}
        for c in ('sens', 'nonsens'):
            s4[v][c] = {'ratio_2020': round(rat(ca(c, ft, 'CN', 2020)), 3), 'ratio_2025': round(rat(ca(c, ft, 'CN', 2025)), 3),
                        'ratio_1920': round(rat(pooled(c, ft, 'CN', P1920)), 3), 'ratio_2425': round(rat(pooled(c, ft, 'CN', P2425)), 3),
                        'change_2020_2025': r1(chg(c, ft, 'CN', (2020,), (2025,))), 'change_1920_2425': r1(chg(c, ft, 'CN', P1920, P2425)),
                        'comp_mean_ratio_1920': round(st.mean(rat(pooled(c, ft, q_, P1920)) for q_ in C5_COMPS), 3),
                        'comp_mean_ratio_2425': round(st.mean(rat(pooled(c, ft, q_, P2425)) for q_ in C5_COMPS), 3),
                        'cn_share_of_class_2025': r1(100 * ca(c, ft, 'CN', 2025)[2] / ca(c, ft, 'CN', 2025)[3], 2)}
    out['step4_sensitive'] = s4
    # ---- step 7: selection / representativeness
    s7 = {'by_year': [], 'pooled': {}}
    def cov(y_or_ys):
        ys = y_or_ys if isinstance(y_or_ys, tuple) else (y_or_ys,)
        t = {v: pooled('all', int(v == 'ft'), 'CN', ys) for v in V}
        (ffn, fFN, fn_, fN), (afn, aFN, an, aN) = t['ft'], t['all']
        g = lambda x, y: r1(100 * x / y, 1)
        return {'cn_funded': g(ffn, afn), 'cn_other': g(fn_ - ffn, an - afn), 'noncn_funded': g(fFN - ffn, aFN - afn),
                'noncn_other': g((fN - fFN) - (fn_ - ffn), (aN - aFN) - (an - afn)), 'all_ca': g(fN, aN),
                'cn_all': g(fn_, an), 'noncn_all': g(fN - fn_, aN - an),
                'cn_share_ft': g(fn_, fN), 'cn_share_all': g(an, aN), 'funded_share_ft': g(fFN, fN), 'funded_share_all': g(aFN, aN)}
    for y in YEARS: s7['by_year'].append({'y': y, **cov(y)})
    for name, ys in (('2019-20', P1920), ('2024-25', P2425), ('2018-20', P1820), ('2023-25', P2325)): s7['pooled'][name] = cov(ys)
    sens_share = {v: {y: r1(100 * A[('sens', 0, int(v == 'ft'), y)]['CA'] / A[('all', 0, int(v == 'ft'), y)]['CA'], 1) for y in (2020, 2025)} for v in V}
    s7['sensitive_share_of_CA_articles'] = sens_share
    out['step7_selection'] = s7
    # ---- step 7b: tri-agency field rate on CA-CN and other Canadian papers with / without full text, by full-text flag
    # (has_fulltext vs has_content.grobid_xml, which the recall study used; all team sizes and authors_count<51)
    flags = {'has_fulltext': ',has_fulltext:true', 'not_has_fulltext': ',has_fulltext:false',
             'grobid': ',has_content.grobid_xml:true', 'not_grobid': ',has_content.grobid_xml:false',
             'fulltext_not_grobid': ',has_fulltext:true,has_content.grobid_xml:false', 'none': ''}
    jobs = [(fl, fu, per, small) for fl in flags for fu in (0, 1) for per in ('2018-2020', '2023-2025') for small in (0, 1)]
    def j7(j):
        fl, fu, per, small = j
        f = f'type:article,institutions.country_code:CA,publication_year:{per}' + flags[fl] + (f',funders.id:{CA_FUND}' if fu else '') + \
            (',authors_count:<51' if small else '')
        return j, grp(f, 'institutions.country_code')
    R7 = {}
    with cf.ThreadPoolExecutor(4) as ex:
        for j, d in ex.map(j7, jobs): R7[j] = d
    s7b = {}
    for small in (0, 1):
        for per in ('2018-2020', '2023-2025'):
            for fl in flags:
                a, f_ = R7[(fl, 0, per, small)], R7[(fl, 1, per, small)]
                cn_n, cn_f, ca_n, ca_f = a.get('CN', 0), f_.get('CN', 0), a['CA'], f_['CA']
                s7b[f"{'lt51' if small else 'allsizes'} {per} {fl}"] = {
                    'cn_n': cn_n, 'cn_funded': cn_f, 'cn_field_rate': r1(100 * cn_f / cn_n, 1) if cn_n else None,
                    'noncn_n': ca_n - cn_n, 'noncn_field_rate': r1(100 * (ca_f - cn_f) / (ca_n - cn_n), 1)}
    out['step7b_field_rate_by_flag'] = s7b
    # ---- step 7c: bridge. Rebuild the all-papers ratio with the field's recall corrected separately on full-text and
    # non-full-text papers (true funded = field funded / recall). Full-text recall from the hand-checked recall study (CA-CN .97 -> .93,
    # CA-US as the non-CN proxy .88 -> .905); non-full-text recall = Crossref's, in that study's variants (MANIFEST.md).
    def cellsP(ys):
        fn_ft, FN_ft, n_ft, N_ft = pooled('all', 1, 'CN', ys)   # full text: (funded CN, funded, CN, all)
        fn, FN, n, N = pooled('all', 0, 'CN', ys)               # all papers
        return {'cnf_ft': fn_ft, 'cnf_nft': fn - fn_ft, 'cn_ft': n_ft, 'cn_nft': n - n_ft,
                'nf_ft': FN_ft - fn_ft, 'nf_nft': (FN - fn) - (FN_ft - fn_ft), 'n_ft': N_ft - n_ft, 'n_nft': (N - n) - (N_ft - n_ft)}
    def tratio(c, r1c, r0c, r1n, r0n):
        tcn = c['cnf_ft'] / r1c + c['cnf_nft'] / r0c; tn = c['nf_ft'] / r1n + c['nf_nft'] / r0n
        CN, NN = c['cn_ft'] + c['cn_nft'], c['n_ft'] + c['n_nft']
        return (tcn / (tcn + tn)) / ((CN - tcn) / ((CN - tcn) + (NN - tn)))
    pre_c, post_c = cellsP(P1920), cellsP(P2425)
    variants = {'field as recorded': ((1, 1, 1, 1), (1, 1, 1, 1)),
                'non-full-text recall = full-text recall': ((.97, .97, .88, .88), (.93, .93, .905, .905)),
                'non-full-text recall = Crossref pooled 0.60': ((.97, .60, .88, .60), (.93, .60, .905, .60)),
                'non-full-text recall = Crossref by stratum (CN .61 -> .66; non-CN as CA-US .53 -> .63)': ((.97, .61, .88, .53), (.93, .66, .905, .63))}
    out['step7c_recall_corrected_all_papers'] = {'cells_2019-20': pre_c, 'cells_2024-25': post_c,
        'ratio_change_1920_2425': {k: r1(100 * (tratio(post_c, *b) / tratio(pre_c, *a) - 1)) for k, (a, b) in variants.items()}}
    json.dump(out, open(os.path.join(D, 'funded_fulltext.json'), 'w'), indent=1)
    # ---- chart rows
    f1 = []
    for p in F1_PARTNERS:
        for y in YEARS:
            fs, os_ = shares(ca('all', 1, p, y)); fa, oa_ = shares(ca('all', 0, p, y))
            f1.append({'p': NAMES[p], 'y': y, 'f': round(fs, 2), 'o': round(os_, 2), 'f_all': round(fa, 2), 'o_all': round(oa_, 2)})
    json.dump(f1, open(os.path.join(D, 'chart_funded_fulltext_f1.json'), 'w'))
    lines = []
    for y in YEARS:
        t = ca('all', 1, 'CN', y); fs, os_ = shares(t); fa, oa_ = shares(ca('all', 0, 'CN', y))
        lines.append({'y': y, 'funded': round(fs, 2), 'other': round(os_, 2), 'fn': t[0], 'funded_all': round(fa, 2), 'other_all': round(oa_, 2)})
    bars = sorted([{'p': NAMES[r['p']], 'g': 'concern' if r['p'] in CONCERN else 'comp', 'c': round(r['after_ft']), 'pt': round(r['before_ft']),
                    'c_all': round(r['after_all']), 'pt_all': round(r['before_all'])} for r in s2], key=lambda b: b['c'])
    json.dump({'lines': lines, 'bars': bars}, open(os.path.join(D, 'chart_funded_fulltext_c4.json'), 'w'))
    c5 = []
    for y in YEARS:
        row = {'y': y}
        for v in V:
            sfx = '' if v == 'ft' else '_all'; ft = int(v == 'ft')
            for c in ('sens', 'nonsens'):
                row[c + sfx] = round(rat(ca(c, ft, 'CN', y)), 3)
                row[c + '_comp' + sfx] = round(st.mean(rat(ca(c, ft, q_, y)) for q_ in C5_COMPS), 3)
        c5.append(row)
    json.dump(c5, open(os.path.join(D, 'chart_funded_fulltext_c5.json'), 'w'))
    peers = [{'p': NAMES[c], 'c': s3['ft']['2019-20']['change'][c], 'c_all': s3['all']['2019-20']['change'][c]} for c in PEER_FUND]
    json.dump(sorted(peers, key=lambda r: r['c']), open(os.path.join(D, 'chart_funded_fulltext_peers.json'), 'w'))
    report(out)

def report(o):
    s1 = o['step1_canada_china']
    print('STEP 1 Canada-China (funded share | other share | ratio)')
    for v in ('ft', 'all'):
        for r in s1['by_year'][v]:
            if r['y'] in (2015, 2019, 2020, 2024, 2025):
                print(f"  {v:3} {r['y']} funded {r['funded_share']:5.2f}% ({r['funded_CN']}/{r['funded_N']})  other {r['other_share']:5.2f}%  ratio {r['ratio']:.3f}")
        print('  ', v, s1['changes'][v])
    s2 = o['step2_partners19']
    print('STEP 2 19 partners: after ft | after all | before ft | before all')
    for r in s2['rows']: print(f"  {r['p']} {r['after_ft']:6.1f} {r['after_all']:6.1f} {r['before_ft']:6.1f} {r['before_all']:6.1f}")
    print('  medians after', s2['median_after'], 'before', s2['median_before'], '15 comps after', s2['median_after_15_comparators'])
    print('STEP 3 peers')
    for v in ('ft', 'all'):
        for b in ('2015-16', '2017-18', '2019-20'):
            x = o['step3_peers_cn'][v][b]
            print(f"  {v} base {b}: rank {x['canada_rank_of_9']} median {x['peer_median']} CA-med {x['canada_minus_median_pts']} pts / rel {x['canada_vs_median_relative']}  {x['change']}")
        print('  ', v, o['step3_peers_cn'][v]['ci95_2019-20'])
    print('STEP 4', json.dumps(o['step4_sensitive']))
    print('STEP 7 pooled', json.dumps(o['step7_selection']['pooled'], indent=0))
    print('  sensitive share', o['step7_selection']['sensitive_share_of_CA_articles'])
    print('STEP 7b field rate by flag (CN | non-CN)')
    for k, v in o['step7b_field_rate_by_flag'].items():
        print(f"  {k:45} CN {v['cn_field_rate']} (n {v['cn_n']})  nonCN {v['noncn_field_rate']} (n {v['noncn_n']})")
    print('STEP 7c', o['step7c_recall_corrected_all_papers']['ratio_change_1920_2425'])

if __name__ == '__main__':
    main()
