"""Phase-in: lag between the award year embedded in NSERC (RGPIN-YYYY..., ALLRP etc.), SSHRC (4xx-YYYY-....)
and Canada Research Chairs (CRC-YYYY-...) award numbers and the paper's publication year.
Random samples of 1,000 tri-agency papers with a Canadian author per publication year."""
import re
from collections import Counter
from oa import *
YR_IDS = AG['nserc'] + '|' + AG['sshrc'] + '|F4320320994'
FUN = set('https://openalex.org/' + x for x in YR_IDS.split('|'))
pats = [re.compile(r'^(?:RGPIN|RGPAS|DGECR|ALLRP|CRDPJ|RGPGP|RTI|PGSD\w*|CGS\w*|STPGP|EGP|CREATE|RGPNS|SAPIN|SAPPJ|IRCPJ|CRC|CRC\w*|PDF|NETGP|CRSNG|I2IPJ)[\s\-_]*((?:19|20)\d\d)\b', re.I),
        re.compile(r'^(?:4\d\d|8\d\d|89\d)[\s\-](20\d\d)[\s\-]\d+', re.I)]
def yr(s):
    s = (s or '').strip()
    for p in pats:
        m = p.search(s)
        if m: return int(m.group(1))
out = {}
for py in range(2017, 2026):
    ws = []
    for page in range(1, 6):
        r = get('works', filter=f'{BASE},publication_year:{py},institutions.country_code:CA,awards.funder_id:{YR_IDS}',
                sample=1000, seed=7, per_page=200, page=page, select='id,awards')
        ws += r['results']
    lags_max, lags_all, parsed = Counter(), Counter(), 0
    for w in ws:
        ys = [yr(a['funder_award_id']) for a in w['awards'] if a.get('funder_id') in FUN]
        ys = [y for y in ys if y and 1995 <= y <= py]
        if not ys: continue
        parsed += 1
        lags_max[py - max(ys)] += 1
        for y in ys: lags_all[py - y] += 1
    out[py] = {'sampled': len(ws), 'parsed': parsed, 'lag_newest_award': dict(lags_max), 'lag_all_awards': dict(lags_all)}
    tot = sum(lags_max.values())
    cum = 0; s = []
    for L in range(0, 11):
        cum += lags_max.get(L, 0); s.append(f'{L}:{100*cum/tot:.0f}')
    print(py, len(ws), parsed, ' '.join(s))
save('s1_phasein_lags.json', out)
