"""Chart rows for two charts in the post that are not written by their analysis scripts.
C1 (share of Canadian articles with a co-author in each country) from ../results/pairs.json (pull_pairs.py);
F2 (listed-organization index, funded vs other) from ../results/nro_funded_split_verified.json (nro_funded_split.py).
Outputs ../results/chart_c1_shares.json, ../results/chart_f2_nro_split.json"""
import json
P = json.load(open('../results/pairs.json'))
Y = [str(y) for y in range(2010, 2026)]
NAMES = {'CN': 'China', 'HK': 'Hong Kong', 'IR': 'Iran', 'RU': 'Russia', 'US': 'United States', 'GB': 'United Kingdom',
         'DE': 'Germany', 'IN': 'India'}
c1 = [{'p': NAMES[p], 'g': 'concern' if p in ('CN', 'HK', 'IR', 'RU') else 'comp', 'y': int(t),
       'v': round(100 * P['all']['CA'][t][p] / P['all']['CA'][t]['CA'], 2)}
      for p in ['CN', 'HK', 'IR', 'RU', 'US', 'GB', 'DE', 'IN'] for t in Y]
json.dump(c1, open('../results/chart_c1_shares.json', 'w'))
# 2026 so far: Jan-Oct shares quoted in the text
for k in ('ytd2024', 'ytd2025', 'ytd2026'):
    r = P['all']['CA'][k]
    print(k, ' '.join(f"{p}:{100 * r[p] / r['CA']:.1f}%" for p in ('CN', 'IR', 'RU', 'HK')))
S = json.load(open('../results/nro_funded_split_verified.json'))
f2 = [{'y': int(t), 'f': S['funded'][t], 'o': S['other'][t], 'nf': S['funded_counts'][t]['nro'], 'no': S['other_counts'][t]['nro']}
      for t in sorted(S['funded'])]
json.dump(f2, open('../results/chart_f2_nro_split.json', 'w'))
print('chart rows written')
