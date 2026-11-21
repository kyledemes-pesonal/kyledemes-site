"""NRO index split by funded vs other Canadian papers (works, not links), from the local download
(authors_count<51). Index = (NRO works / control works) / (NRO own output / control own output), 2018-20 = 100.
Run with VERIFIED=1 after author_panel.py (VERIFIED=1) and nro_own_output.py. Output ../results/nro_funded_split_verified.json"""
import json, math
P = json.load(open('../results/author_panel'+('_verified' if __import__('os').environ.get('VERIFIED')=='1' else '')+'.json'))['index']; R = json.load(open('../results/nro_own_output.json'))
Y = [str(y) for y in range(2015, 2026)]
own = {t: R['own_nro'][t] / R['own_ctl'][t] for t in Y}
out = {}
for t_ in Y:
    for m in ('nro', 'ctl', 'all'): P[t_][m + '_a'] = P[t_].get(m + '_f', 0) + P[t_].get(m + '_o', 0)
for k, lab in (('f', 'funded'), ('o', 'other'), ('a', 'all')):
    raw = {t: (P[t]['nro_' + k] / P[t]['ctl_' + k]) / own[t] for t in Y}
    base = sum(raw[t] for t in ('2018', '2019', '2020')) / 3
    out[lab] = {t: round(100 * raw[t] / base, 1) for t in Y}
    out[lab + '_counts'] = {t: {'nro': P[t]['nro_' + k], 'ctl': P[t]['ctl_' + k], 'all': P[t]['all_' + k]} for t in Y}
json.dump(out, open('../results/nro_funded_split'+('_verified' if __import__('os').environ.get('VERIFIED')=='1' else '')+'.json', 'w'))
for lab in ('funded', 'other', 'all'):
    print(lab, ' '.join(f"{t[2:]}:{out[lab][t]}" for t in Y))
    print('   nro works', ' '.join(f"{t[2:]}:{out[lab+'_counts'][t]['nro']}" for t in Y))
print('total works in download', sum(P[t]['all_f'] + P[t]['all_o'] for t in Y))
