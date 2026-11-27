"""v3 (22 Nov 2026): writes scripts/v3_q14_citing_pool_coverage.sql, v2 Q11's citing-pool reference coverage for the v3 pure
set (results/v3/stacks_v3.tsv): treated journals vs their controls. Same definitions as v2_make_q11.py."""
import os, re
import pandas as pd
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
st = pd.read_csv('results/v3/stacks_v3.tsv', sep='\t'); p = st[st.group == 'pure']
T = sorted(set(p.treated)); C = sorted(set(int(c) for cs in p.controls for c in cs.split()) - set(T))
q = open('scripts/v2_q11_citing_pool_coverage.sql').read()
q = q.replace('-- v2 Q11:', '-- v3 Q14 (v3 pure set):')
q = re.sub(r'WHEN src IN \([0-9,]+\)', 'WHEN src IN (' + ','.join(map(str, T)) + ')', q, count=1)
q = re.sub(r'WHERE src IN \([0-9,]+\)\)', 'WHERE src IN (' + ','.join(map(str, T + C)) + '))', q, count=1)
q = re.sub(r'treated \(\d+ pure-opening journals\) vs their controls \(\d+ journals\)', f'treated ({len(T)} pure-opening journals) vs their controls ({len(C)} journals)', q)
open('scripts/v3_q14_citing_pool_coverage.sql', 'w').write(q); print(len(T), len(C))
