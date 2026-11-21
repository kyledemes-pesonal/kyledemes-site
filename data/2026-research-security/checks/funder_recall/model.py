"""Step 6: whole-stratum estimate. Full-text works: true share from acknowledgement text. Works without full text: OpenAlex's
field there is essentially Crossref's deposit (checked on 250 per stratum), so true share = field share / r_n, where r_n is the
recall of Crossref deposits measured on full-text works (variants below). Combines by full-text coverage from candidates.csv.
Bootstrap (2,000) over works within each stratum. Output model.json"""
import csv, json, os, random, collections, re
HERE = os.path.dirname(os.path.abspath(__file__))
STRATA = ['CA-CN 2018-20', 'CA-CN 2023-25', 'CA-US 2018-20', 'CA-US 2023-25']
C = list(csv.DictReader(open(f'{HERE}/candidates.csv')))
P = {r['work_id']: r for r in csv.DictReader(open(f'{HERE}/per_work.csv'))}
CR = {json.loads(l)['work_id']: json.loads(l) for l in open(f'{HERE}/crossref.jsonl')}
def pubgrp(wid):
    p = ((CR.get(wid) or {}).get('publisher') or '').lower()
    for k in ['elsevier', 'springer', 'wiley', 'ieee', 'taylor', 'mdpi', 'frontiers', 'oxford', 'american chemical', 'sage', 'public library', 'bmj', 'wolters', 'iop', 'american physical']:
        if k in p: return k
    return 'other'
data = {}
for s in STRATA:
    cs = [c for c in C if c['stratum'] == s and c['has_grobid'] in ('0', '1')]
    ft = [P[c['work_id']] for c in cs if c['has_grobid'] == '1' and c['work_id'] in P]
    nf = [c for c in cs if c['has_grobid'] == '0']
    data[s] = {'cov': (sum(c['has_grobid'] == '1' for c in cs), len(cs)),
               # full-text works: (ack_tri, field, crossref_tri, publisher group); unusable counted as ack_tri 0
               'ft': [(int(r['ack_tri']) if r['usable'] == '1' else 0, int(r['field_tri_local']), int(r['crossref_tri'] or 0) if r['crossref_tri'] != '' else None, pubgrp(r['work_id'])) for r in ft],
               'nf': [(int(c['field_tri_local']), pubgrp(c['work_id']) if c['work_id'] in CR else None) for c in nf]}
def est(d, variant, pooled_r=None):
    out = {}
    for s in STRATA:
        D = d[s]; ft = D['ft']; nf = D['nf']
        c = D['cov'][0] / D['cov'][1]
        t_ft = sum(x[0] for x in ft) / len(ft); f_ft = sum(x[1] for x in ft) / len(ft)
        f_n = sum(x[0] for x in nf) / len(nf)
        A = [x for x in ft if x[0] == 1 and x[2] is not None]
        if variant == 'crossref_recall_by_stratum':
            r_n = sum(x[2] for x in A) / len(A)
        elif variant == 'crossref_recall_pooled':
            r_n = pooled_r
        elif variant == 'publisher_weighted':
            byp = collections.defaultdict(list)
            for s2 in STRATA:   # publisher-level Crossref recall, pooled over strata within the same period
                if s2[-7:] == s[-7:]:
                    for x in d[s2]['ft']:
                        if x[0] == 1 and x[2] is not None: byp[x[3]].append(x[2])
            allr = [v for L in byp.values() for v in L]; base = sum(allr) / len(allr)
            nfp = [x for x in nf if x[1] is not None]
            # Crossref recall by publisher (shrunk to the period mean, 5 pseudo-works), weighted by the non-full-text publisher mix
            w = collections.Counter(x[1] for x in nfp)   # publisher mix of all non-full-text works
            num = sum(n * ((sum(byp[p]) + 5 * base) / (len(byp[p]) + 5)) for p, n in w.items()); r_n = num / sum(w.values())
        elif variant == 'same_as_fulltext':
            r_n = sum(1 for x in ft if x[0] == 1 and x[1] == 1) / max(1, sum(x[0] for x in ft))
        t_n = min(1, f_n / r_n)
        out[s] = {'coverage': c, 'true_ft': t_ft, 'field_ft': f_ft, 'field_nonft': f_n, 'r_nonft': r_n, 'true_nonft': t_n,
                  'true': c * t_ft + (1 - c) * t_n, 'field': c * f_ft + (1 - c) * f_n}
        out[s]['recall_overall'] = out[s]['field'] / out[s]['true']
    for k in ['true', 'field']:
        cn = out['CA-CN 2023-25'][k] / out['CA-CN 2018-20'][k]; us = out['CA-US 2023-25'][k] / out['CA-US 2018-20'][k]
        out[f'{k}_CN_change'] = cn - 1; out[f'{k}_US_change'] = us - 1; out[f'{k}_CN_vs_US'] = cn / us - 1
    out['bias_pts'] = out['field_CN_vs_US'] - out['true_CN_vs_US']
    # anchored to the whole-stratum field rates from the local download (removes sampling noise in the field side)
    POP = json.load(open(f'{HERE}/population.json'))
    tp = {s: POP[s]['field_tri_rate'] / out[s]['recall_overall'] for s in STRATA}
    cn = tp['CA-CN 2023-25'] / tp['CA-CN 2018-20']; us = tp['CA-US 2023-25'] / tp['CA-US 2018-20']
    out['pop_true'] = tp; out['pop_true_CN_vs_US'] = cn / us - 1; out['pop_true_CN_change'] = cn - 1; out['pop_true_US_change'] = us - 1
    return out
allA = [x for s in STRATA for x in data[s]['ft'] if x[0] == 1 and x[2] is not None]
pooled = sum(x[2] for x in allA) / len(allA)
res = {'pooled_crossref_recall': pooled}
rng = random.Random(11)
for v in ['crossref_recall_by_stratum', 'crossref_recall_pooled', 'publisher_weighted', 'same_as_fulltext']:
    pt = est(data, v, pooled)
    bs = []
    for b in range(1000):
        d2 = {s: {'cov': data[s]['cov'], 'ft': [rng.choice(data[s]['ft']) for _ in data[s]['ft']], 'nf': [rng.choice(data[s]['nf']) for _ in data[s]['nf']]} for s in STRATA}
        bs.append(est(d2, v, pooled))
    for k in ['true_CN_vs_US', 'field_CN_vs_US', 'bias_pts', 'true_CN_change', 'true_US_change', 'pop_true_CN_vs_US', 'pop_true_CN_change', 'pop_true_US_change']:
        vals = sorted(x[k] for x in bs); pt[k + '_ci'] = (vals[25], vals[974])
    res[v] = pt
    print(f"\n== {v}")
    for s in STRATA:
        o = pt[s]; print(f"  {s}: cov {o['coverage']:.1%} | ft true {o['true_ft']:.1%} field {o['field_ft']:.1%} | nonft field {o['field_nonft']:.1%} r_n {o['r_nonft']:.2f} true {o['true_nonft']:.1%} | TOTAL true {o['true']:.1%} field {o['field']:.1%} recall {o['recall_overall']:.2f}")
    print(f"  CN change true {pt['true_CN_change']:+.1%} {pt['true_CN_change_ci']} field {pt['field_CN_change']:+.1%}; US true {pt['true_US_change']:+.1%} field {pt['field_US_change']:+.1%}")
    print(f"  POPULATION-anchored: true CN {pt['pop_true_CN_change']:+.1%} {tuple(round(x,3) for x in pt['pop_true_CN_change_ci'])} US {pt['pop_true_US_change']:+.1%} {tuple(round(x,3) for x in pt['pop_true_US_change_ci'])} CN vs US {pt['pop_true_CN_vs_US']:+.1%} {tuple(round(x,3) for x in pt['pop_true_CN_vs_US_ci'])}  (field: CN -32.5%, US -2.3%, CN vs US -30.9%)")
    print(f"  CN vs US: true {pt['true_CN_vs_US']:+.1%} {tuple(round(x,3) for x in pt['true_CN_vs_US_ci'])}  field {pt['field_CN_vs_US']:+.1%}  bias {pt['bias_pts']:+.3f} {tuple(round(x,3) for x in pt['bias_pts_ci'])}")
json.dump(res, open(f'{HERE}/model.json', 'w'), indent=1)
