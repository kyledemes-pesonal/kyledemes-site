"""Triple-difference / event study on country-pair co-authorship.
r[f,p,t] = log(n_fpt / N_ft) - mean_{q in comparators, q!=f} log(n_fqt / N_ft)
  (Canada's intensity with partner p relative to its intensity with comparator partners)
Event-study coefficient for focal f, partner p, year t, base B (mean of 2018-2020):
  b[f,p,t] = (r[f,p,t]-r[f,p,B]) - mean_{g in peers, g!=f} (r[g,p,t]-r[g,p,B])
This equals the OLS estimate of a pair-FE + partner-year FE + focal-year FE model on a balanced panel.
Placebo inference: compute b for every peer as if treated (vs the other peers).
"""
import json, math, sys
d = json.load(open('../results/pairs.json'))
FOCAL = ['CA','US','GB','AU','DE','FR','JP','NL']
COMP = ['US','GB','DE','FR','AU','JP','IT','NL','CH','SE','ES','KR','IN','BR','TR']
CONCERN = ['CN','HK','IR','RU']
YEARS = list(range(2010, 2026))
def r(spec, f, p, t):
    row = d[spec][f][str(t)]; N = row[f]
    comps = [q for q in COMP if q != f]
    base = sum(math.log(row[q]/N) for q in comps)/len(comps)
    return math.log(row[p]/N) - base
def es(spec, f, p, B=(2018, 2019, 2020), peers=None):
    peers = [g for g in (peers or FOCAL) if g != f]
    out = {}
    for t in YEARS:
        rb = lambda ff: sum(r(spec,ff,p,b) for b in B)/len(B)   # base = mean of 2018-2020
        own = r(spec,f,p,t) - rb(f)
        oth = sum(r(spec,g,p,t) - rb(g) for g in peers)/len(peers)
        out[t] = own - oth
    return out
if __name__ == '__main__':
    res = {}
    for spec in ['all','small','core']:
        res[spec] = {}
        for p in CONCERN + ['IN','KR','US']:
            res[spec][p] = {f: es(spec, f, p) for f in FOCAL}
    json.dump(res, open('../results/event_study.json','w'), indent=0)
    for spec in ['all','small','core']:
        print('==', spec)
        for p in CONCERN + ['IN','KR']:
            print(p, ' '.join(f"{t}:{100*(math.exp(res[spec][p]['CA'][t])-1):+.0f}%" for t in [2012,2015,2018,2019,2021,2022,2023,2024,2025]))
            # placebo rank of 2025 and 2024-25 average
            v = {f: (res[spec][p][f][2024]+res[spec][p][f][2025])/2 for f in FOCAL}
            rank = sorted(v, key=v.get)
            print('   2024-25 avg by focal:', ' '.join(f"{f}:{100*(math.exp(v[f])-1):+.0f}%" for f in rank))
