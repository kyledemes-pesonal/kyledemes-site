"""Who leads Canada-China papers? From the local Canadian article download (2015-2025, authors_count<51).
For works with at least one Canadian and one Chinese (mainland, CN) authorship: classify the first and the last
author as Canadian-only, Chinese-only, both (dual affiliation), or neither. Split by tri-agency/CFI funding, by
verified named-organization (NRO) works, and compare with Canada-US papers. Works with a single author skipped.
Output ../results/lead_author.json"""
import json, collections, csv, sys
sys.argv = sys.argv[:1]
import author_panel as ap   # reuses works(), FUND, VER_CN (needs VERIFIED=1 env for VER_CN)
def who(a, c):
    cc = set(a[3]); ca, xx = 'CA' in cc, c in cc
    return 'both' if ca and xx else 'ca' if ca else 'x' if xx else 'other'
res = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))
seen = set()
for w in ap.works():
    if w['w'] in seen or not w['y'] or len(w['a']) < 2: continue
    seen.add(w['w'])
    fu = bool(set(w['f']) & ap.FUND); allc = set().union(*[set(a[3]) for a in w['a']])
    for c in ('CN', 'US'):
        if c not in allc or 'CA' not in allc: continue
        groups = [f'{c}_all', f"{c}_{'funded' if fu else 'other'}"]
        if c == 'CN' and w['w'] in ap.VER_CN: groups += ['NRO_all', f"NRO_{'funded' if fu else 'other'}"]
        f, l = who(w['a'][0], c), who(w['a'][-1], c)
        for g in groups:
            k = res[g][w['y']]; k['n'] += 1; k['first_' + f] += 1; k['last_' + l] += 1
            k['ca_leads'] += (l in ('ca', 'both')) or (f in ('ca', 'both'))
out = {g: {str(y): dict(c) for y, c in sorted(d.items())} for g, d in res.items()}
json.dump(out, open('../results/lead_author.json', 'w'))
for g in ('CN_all', 'CN_funded', 'CN_other', 'NRO_all', 'NRO_funded', 'US_all'):
    print('==', g, ' year n  first:CA/CN/both  last:CA/CN/both  (%)')
    for y, c in sorted(res[g].items()):
        n = c['n']; p = lambda k: 100 * c[k] / n
        print(f"{y} {n:6d}  {p('first_ca'):4.0f} {p('first_x'):4.0f} {p('first_both'):4.0f}   {p('last_ca'):4.0f} {p('last_x'):4.0f} {p('last_both'):4.0f}")
