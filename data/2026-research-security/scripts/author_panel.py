"""Author panel and funded/other split of the named-organization (NRO) index, from the local download of
Canadian articles 2015-2025 (authors_count < 51; ../results/ca_works, built by pull_ca_works.py).

Definitions
- Canadian authorship: an authorship with an institution in CA.
- NRO work: any authorship on the work has an NRO (high/medium match) in its institution lineage.
- Control work: any authorship has one of the 247 unlisted Chinese control institutions in its lineage.
- Funded: the work credits NSERC, CIHR, SSHRC or CFI (same funder IDs as everywhere else).
- Cohort A: authors with a Canadian authorship on an NRO work published 2018-2020.
- Cohort B (control): authors with a Canadian authorship on a control work in 2018-2020 and no Canadian
  authorship on any NRO work 2015-2020.
- Outcomes per author-year: Canadian-affiliated papers (all, funded), and of those, NRO / control / any-China
  papers (all, funded).
Output: ../results/author_panel.json
"""
import gzip, json, glob, csv, collections, sys
D = '../results'
FUND = {'F4320334593', 'F4320334506', 'F4320334617', 'F7697234222', 'F4320319952', 'F4320320995'}
nro_rows = [r for r in csv.DictReader(open(f'{D}/nro_map.csv')) if r['confidence'] in ('high', 'medium')]
NRO = {'CN': set(), 'IR': set(), 'RU': set()}
for r in nro_rows:
    NRO[r['country']].add(r['openalex_id'])
    for c in r['child_ids'].replace('|', ';').split(';'):
        if c.strip(): NRO[r['country']].add(c.strip())
NRO_CN = NRO['CN']; NRO_ALL = NRO['CN'] | NRO['IR'] | NRO['RU']
import os
VERIFIED = os.environ.get('VERIFIED') == '1'   # count a work as NRO only if data/nro_verification.csv verified it for a Chinese NRO (nro_verification_verdicts.csv)
SUF = '_verified' if VERIFIED else ''
VER_CN = set()
# Affiliated hospitals are NOT counted with their university: strings match institutions; only a ROR
# lineage link makes a hospital part of a university.
if VERIFIED:
    for r in csv.DictReader(open(f'{D}/nro_verification_verdicts.csv')):
        if r['verdict'] == 'verified' and set(r['nro_ids'].split(';')) & NRO_CN: VER_CN.add(r['work_id'])
UMB = {'Chinese Academy of Sciences', 'Ministry of Industry and Information Technology', 'University of Science and Technology of China'}
CTRL = {r['id'] for r in csv.DictReader(open(f'{D}/nro_controls.csv'))
        if r['country'] == 'CN' and r['display_name'] not in UMB and r['has_nro_below'] in ('', 'False', 'false', '0')}

def works(years=None):
    for fn in sorted(glob.glob(f'{D}/ca_works/*.jsonl.gz')):
        if years and int(fn.rsplit('/', 1)[1][:4]) not in years: continue
        with gzip.open(fn, 'rt') as fh:
            for line in fh:
                try: yield json.loads(line)
                except json.JSONDecodeError: pass

def flags(w):
    lins = [set(a[2]) for a in w['a']]
    nro = (w['w'] in VER_CN) if VERIFIED else any(l & NRO_CN for l in lins); ctl = any(l & CTRL for l in lins)
    cn = any('CN' in a[3] for a in w['a'])
    return nro, ctl, cn, bool(set(w['f']) & FUND)

if __name__ == '__main__':  # importing (lead_author.py, provinces.py) must not rerun the panel
    # ---- pass 1: cohorts, plus the work-level NRO index split by funding
    A, B_cand, nro_pre = set(), set(), set()
    orcid = {}
    index = collections.defaultdict(lambda: collections.Counter())
    seen = set()
    for w in works():
        if w['w'] in seen: continue
        seen.add(w['w'])
        y = w['y']; nro, ctl, cn, fu = flags(w)
        k = 'f' if fu else 'o'
        index[y]['all_' + k] += 1
        if nro: index[y]['nro_' + k] += 1
        if ctl: index[y]['ctl_' + k] += 1
        if cn: index[y]['cn_' + k] += 1
        if y is None or y > 2020: continue
        ca = [a for a in w['a'] if 'CA' in a[3] and a[0]]
        for a in ca: orcid[a[0]] = orcid.get(a[0], False) or a[1]
        if nro:
            for a in ca:
                nro_pre.add(a[0])
                if 2018 <= y <= 2020: A.add(a[0])
        if ctl and 2018 <= y <= 2020:
            for a in ca: B_cand.add(a[0])
    B = B_cand - nro_pre
    print('cohort A', len(A), 'cohort B', len(B), file=sys.stderr)

    # ---- pass 2: outcomes per author-year for cohort authors
    K = ['n', 'nf', 'nro', 'nro_f', 'ctl', 'ctl_f', 'cn', 'cn_f']
    panel = {a: collections.defaultdict(lambda: [0] * 8) for a in A | B}
    seen = set()
    for w in works():
        if w['w'] in seen: continue
        seen.add(w['w'])
        ids = {a[0] for a in w['a'] if 'CA' in a[3] and a[0] in panel}
        if not ids: continue
        nro, ctl, cn, fu = flags(w)
        v = [1, fu, nro, nro and fu, ctl, ctl and fu, cn, cn and fu]
        for a in ids:
            row = panel[a][w['y']]
            for i, x in enumerate(v): row[i] += int(bool(x))

    out = {'definitions': __doc__, 'n_A': len(A), 'n_B': len(B),
           'index': {str(y): dict(c) for y, c in sorted(index.items()) if y},
           'orcid_A': sum(orcid.get(a, False) for a in A), 'orcid_B': sum(orcid.get(a, False) for a in B),
           'panel': {g: {a: {str(y): r for y, r in panel[a].items()} for a in S} for g, S in (('A', A), ('B', B))},
           'orcid': {a: orcid.get(a, False) for a in A | B}}
    json.dump(out, open(f'{D}/author_panel{SUF}.json', 'w'))
    print('done', file=sys.stderr)
