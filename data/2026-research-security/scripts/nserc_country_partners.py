"""NSERC grants (grant-years) with at least one partner organization in a given country, by fiscal year,
FY2012-2024, from the NSERC open-data partner files. Output ../results/nserc_country_partners.json"""
import csv, io, glob, json, collections
from nserc_huawei import rows
D = '../results'
apps = collections.defaultdict(lambda: collections.defaultdict(set)); allapps = collections.defaultdict(set)
names = collections.defaultdict(collections.Counter)
for fn in sorted(glob.glob(f'{D}/nserc_partners_raw/partner_*.csv')):
    for r in rows(fn):
        fy = int(r['FiscalYear'][:4]); c = (r.get('CountryEN') or '').strip().upper()
        allapps[fy].add(r['ApplicationID']); apps[c][fy].add(r['ApplicationID'])
        if c == 'CHINA': names[r['PartInstitution']][fy] += 1
yrs = range(2012, 2025)
out = {'all': {y: len(allapps[y]) for y in yrs}, 'by_country': {c: {y: len(d[y]) for y in yrs} for c, d in apps.items()}}
json.dump(out, open(f'{D}/nserc_country_partners.json', 'w'), indent=1)
print('FY      ' + ' '.join(f'{y%100:>5}' for y in yrs))
print('all     ' + ' '.join(f'{len(allapps[y]):5d}' for y in yrs))
for c in ('CHINA', 'HONG KONG', 'UNITED STATES', 'UNITED KINGDOM', 'GERMANY', 'FRANCE', 'JAPAN', 'INDIA', 'IRAN', 'RUSSIA', 'RUSSIAN FEDERATION', 'TAIWAN', 'SOUTH KOREA', 'KOREA, REPUBLIC OF'):
    if c in apps: print(f'{c[:7]:7} ' + ' '.join(f'{len(apps[c][y]):5d}' for y in yrs))
print([c for c in apps if 'CHIN' in c or 'KOREA' in c or 'RUSS' in c or 'HONG' in c])
print('top Chinese partners:', [(n, sum(v.values())) for n, v in sorted(names.items(), key=lambda kv: -sum(kv[1].values()))[:15]])
