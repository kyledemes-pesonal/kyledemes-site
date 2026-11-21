"""Step 5: tables for RECALL.md. Reads candidates.csv, works.csv, meta.jsonl, crossref.jsonl, population.json.
Writes results.json and per_work.csv (sample ids + every decision)."""
import csv, json, math, os, random, re, collections
HERE = os.path.dirname(os.path.abspath(__file__))
FUND = {'F4320334593', 'F4320334506', 'F4320334617', 'F7697234222', 'F4320319952', 'F4320320995'}
CR_DOI = {'10.13039/501100000038': 'NSERC', '10.13039/501100000024': 'CIHR', '10.13039/501100000155': 'SSHRC', '10.13039/501100000196': 'CFI'}
CR_NAME = re.compile(r'\bNSERC\b|\bCIHR\b|\bSSHRC\b|Natural\s+Sciences?\s+and\s+Engineering\s+Research\s+Council|Canadian\s+Institutes?\s+of\s+Health\s+Research|Social\s+Sciences?\s+and\s+Humanities\s+Research\s+Council|Canad(?:a|ian)\s+Foundation\s+for\s+Innovation|Fondation\s+canadienne\s+pour', re.I)
STRATA = ['CA-CN 2018-20', 'CA-CN 2023-25', 'CA-US 2018-20', 'CA-US 2023-25']
def wilson(k, n, z=1.96):
    if n == 0: return (None, None, None)
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (p, max(0, c - h), min(1, c + h))
def newcombe(k1, n1, k2, n2):
    p1, l1, u1 = wilson(k1, n1); p2, l2, u2 = wilson(k2, n2); d = p2 - p1
    return (d, d - math.sqrt((p2 - l2) ** 2 + (u1 - p1) ** 2), d + math.sqrt((u2 - p2) ** 2 + (p1 - l1) ** 2))
C = {r['work_id']: r for r in csv.DictReader(open(f'{HERE}/candidates.csv'))}
W = list(csv.DictReader(open(f'{HERE}/works.csv')))
M = {json.loads(l)['work_id']: json.loads(l) for l in open(f'{HERE}/meta.jsonl')}
CR = {}
for l in open(f'{HERE}/crossref.jsonl'):
    r = json.loads(l); CR[r['work_id']] = r
def cr_tri(wid):
    r = CR.get(wid)
    if not r or not r.get('ok'): return None
    for doi, name, _ in r['funder']:
        d = (doi or '').replace('http://dx.doi.org/', '').replace('https://doi.org/', '')
        if d in CR_DOI or CR_NAME.search(name or ''): return 1
    return 0
pop = json.load(open(f'{HERE}/population.json'))
out = {'population': pop, 'strata': {}, 'compare': {}}
rows = []
for r in W:
    m = M.get(r['work_id'], {})
    r['doi'] = m.get('doi')
    r['field_agencies'] = '|'.join(sorted({ {'F4320334593':'NSERC','F4320334506':'CIHR','F4320334617':'SSHRC','F7697234222':'SSHRC','F4320319952':'CFI','F4320320995':'CFI'}[f] for f, _ in m.get('funders', []) if f in FUND}))
    r['crossref_tri'] = cr_tri(r['work_id'])
    r['crossref_member'] = (CR.get(r['work_id']) or {}).get('publisher')
    rows.append(r)
U = [r for r in rows if r['usable'] == '1']
def stats(L, ackkey='ack_tri'):
    n = len(L); a = [r for r in L if r[ackkey] == '1']; f = [r for r in L if r['field_tri_local'] == '1']
    both = [r for r in a if r['field_tri_local'] == '1']
    acr = [r for r in a if r['crossref_tri'] is not None]
    s = {'n_usable': n, 'ack_tri': wilson(len(a), n), 'field_tri': wilson(len(f), n),
         'recall': wilson(len(both), len(a)), 'n_ack_tri': len(a), 'n_both': len(both),
         'fp_joint': wilson(len(f) - len(both), n), 'field_not_in_text': wilson(len(f) - len(both), len(f)),
         'crossref_recall': wilson(sum(r['crossref_tri'] for r in acr), len(acr)), 'n_ack_tri_crossref': len(acr),
         'field_beyond_crossref_given_ack': wilson(sum(1 for r in acr if r['field_tri_local'] == '1' and r['crossref_tri'] == 0), len(acr))}
    return s
for s in STRATA:
    L = [r for r in U if r['stratum'] == s]
    allL = [r for r in rows if r['stratum'] == s]
    st = stats(L); st['n_downloaded'] = len(allL); st['broad'] = stats(L, 'any_tri_ctx')
    st['crc_only'] = sum(1 for r in L if r['crc'] == '1' and r['ack_tri'] == '0')
    st['crc_only_field'] = sum(1 for r in L if r['crc'] == '1' and r['ack_tri'] == '0' and r['field_tri_local'] == '1')
    # recall by agency
    ag = {}
    for a in ['NSERC', 'CIHR', 'SSHRC', 'CFI']:
        A = [r for r in L if a in r['ack_agencies'].split('|')]
        ag[a] = (len(A), sum(1 for r in A if a in r['field_agencies'].split('|')), sum(1 for r in A if r['field_tri_local'] == '1'))
    st['agency'] = ag
    if s.startswith('CA-CN'):
        for flag, nm in [('1', 'cn_first'), ('0', 'other_first')]:
            st[nm] = stats([r for r in L if r['first_author_cn_only'] == flag])
    # full-text selection
    cs = [c for c in C.values() if c['stratum'] == s and c['has_grobid'] in ('0', '1')]
    g = [c for c in cs if c['has_grobid'] == '1']; ng = [c for c in cs if c['has_grobid'] == '0']
    st['ft_share'] = wilson(len(g), len(cs))
    st['field_rate_ft'] = wilson(sum(c['field_tri_local'] == '1' for c in g), len(g))
    st['field_rate_nonft'] = wilson(sum(c['field_tri_local'] == '1' for c in ng), len(ng))
    nf = [c for c in ng if cr_tri(c['work_id']) is not None]
    st['nonft_crossref'] = {'n': len(nf), 'field': sum(c['field_tri_local'] == '1' for c in nf), 'cr': sum(cr_tri(c['work_id']) for c in nf),
                            'both': sum(1 for c in nf if c['field_tri_local'] == '1' and cr_tri(c['work_id']) == 1),
                            'field_not_cr': sum(1 for c in nf if c['field_tri_local'] == '1' and cr_tri(c['work_id']) == 0),
                            'cr_not_field': sum(1 for c in nf if c['field_tri_local'] == '0' and cr_tri(c['work_id']) == 1)}
    out['strata'][s] = st
S = out['strata']
def k(s, key): return S[s]['n_both'] if key == 'recall' else None
cmp = out['compare']
cmp['recall_CN_change'] = newcombe(S['CA-CN 2018-20']['n_both'], S['CA-CN 2018-20']['n_ack_tri'], S['CA-CN 2023-25']['n_both'], S['CA-CN 2023-25']['n_ack_tri'])
cmp['recall_US_change'] = newcombe(S['CA-US 2018-20']['n_both'], S['CA-US 2018-20']['n_ack_tri'], S['CA-US 2023-25']['n_both'], S['CA-US 2023-25']['n_ack_tri'])
for p in ['2018-20', '2023-25']:
    cmp[f'recall_CN_minus_US_{p}'] = newcombe(S[f'CA-US {p}']['n_both'], S[f'CA-US {p}']['n_ack_tri'], S[f'CA-CN {p}']['n_both'], S[f'CA-CN {p}']['n_ack_tri'])
# share change: ack vs field, bootstrap
rng = random.Random(7)
by = {s: [(int(r['ack_tri']), int(r['field_tri_local']), int(r['any_tri_ctx']), int(r['crossref_tri'] or 0)) for r in U if r['stratum'] == s] for s in STRATA}
def ratios(d):
    res = {}
    for i, nm in [(0, 'ack'), (1, 'field'), (2, 'broad')]:
        sh = {s: sum(x[i] for x in d[s]) / len(d[s]) for s in STRATA}
        cn = sh['CA-CN 2023-25'] / sh['CA-CN 2018-20']; us = sh['CA-US 2023-25'] / sh['CA-US 2018-20']
        res[nm] = {'CN_change': cn - 1, 'US_change': us - 1, 'CN_vs_US': cn / us - 1}
    res['field_minus_ack_CN_vs_US'] = res['field']['CN_vs_US'] - res['ack']['CN_vs_US']
    return res
point = ratios(by)
boots = []
for b in range(2000):
    boots.append(ratios({s: [rng.choice(by[s]) for _ in by[s]] for s in STRATA}))
def ci(f):
    v = sorted(f(x) for x in boots); return (v[50], v[1949])
for nm in ['ack', 'field', 'broad']:
    for q in ['CN_change', 'US_change', 'CN_vs_US']:
        point[nm][q] = (point[nm][q],) + ci(lambda x: x[nm][q])
point['field_minus_ack_CN_vs_US'] = (point['field_minus_ack_CN_vs_US'],) + ci(lambda x: x['field_minus_ack_CN_vs_US'])
cmp['share_changes_fulltext_sample'] = point
# population (local download, all works) field shares for reference
cn = pop['CA-CN 2023-25']['field_tri_rate'] / pop['CA-CN 2018-20']['field_tri_rate']; us = pop['CA-US 2023-25']['field_tri_rate'] / pop['CA-US 2018-20']['field_tri_rate']
cmp['population_field'] = {'CN_change': cn - 1, 'US_change': us - 1, 'CN_vs_US': cn / us - 1}
json.dump(out, open(f'{HERE}/results.json', 'w'), indent=1, default=str)
keep = ['stratum', 'rank', 'work_id', 'doi', 'year', 'first_author_cn_only', 'oa_status', 'usable', 'ack_len', 'ack_tri', 'ack_agencies', 'any_tri_ctx', 'any_agencies',
        'field_tri_local', 'field_tri_live', 'field_agencies', 'crossref_tri', 'crossref_member', 'crc', 'other_cdn_program', 'conflict_only_tri', 'snippet', 'any_snippet']
with open(f'{HERE}/per_work.csv', 'w', newline='') as fh:
    wr = csv.DictWriter(fh, fieldnames=keep, extrasaction='ignore'); wr.writeheader(); wr.writerows(rows)
f3 = lambda t: '%.1f%% [%.1f, %.1f]' % tuple(100 * x for x in t) if t[0] is not None else 'n/a'
for s in STRATA:
    st = S[s]
    print(s, 'dl', st['n_downloaded'], 'usable', st['n_usable'], '| ack', f3(st['ack_tri']), '| field', f3(st['field_tri']), '| recall', f3(st['recall']), f'({st["n_both"]}/{st["n_ack_tri"]})',
          '| fp', f3(st['fp_joint']), '| field-not-in-text', f3(st['field_not_in_text']), '| CR recall', f3(st['crossref_recall']), '| beyond CR', f3(st['field_beyond_crossref_given_ack']))
    print('   broad recall', f3(st['broad']['recall']), 'broad ack', f3(st['broad']['ack_tri']), '| ft share', f3(st['ft_share']), 'field ft', f3(st['field_rate_ft']), 'nonft', f3(st['field_rate_nonft']), '| nonft CR', st['nonft_crossref'], '| agency', st['agency'], 'crc_only', st['crc_only'], st['crc_only_field'])
    for nm in ['cn_first', 'other_first']:
        if nm in st: print('   ', nm, 'n', st[nm]['n_usable'], 'ack', f3(st[nm]['ack_tri']), 'field', f3(st[nm]['field_tri']), 'recall', f3(st[nm]['recall']), st[nm]['n_both'], st[nm]['n_ack_tri'])
print(json.dumps(cmp, indent=1, default=lambda x: x))
