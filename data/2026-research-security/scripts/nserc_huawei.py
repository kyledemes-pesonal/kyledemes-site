"""NSERC grants with Huawei as a partner organization, by lead institution and fiscal year (FY2012-2024).
Partner files (nserc_partners_raw/partner_YYYY.csv) list partner orgs per ApplicationID; the award files
(nserc_raw/award_YYYY.csv, FY2013-2024) give the lead institution, program and amount. Inputs: NSERC open data, downloaded into ../results/nserc_raw/ and
../results/nserc_partners_raw/ (links in MANIFEST.md). Output ../results/nserc_huawei_summary.json (counts only;
grant-level rows with applicant names and titles stay in NSERC's own open data)."""
import csv, io, glob, json, collections
D = '../results'
def rows(fn):
    raw = open(fn, 'rb').read()
    for enc in ('utf-8-sig', 'cp1252', 'latin-1'):
        try: txt = raw.decode(enc); break
        except UnicodeDecodeError: pass
    for r in csv.DictReader(io.StringIO(txt)):
        yield {k.split('-')[0].strip(): v for k, v in r.items() if k}

def main():
    aw = {}
    for fn in sorted(glob.glob(f'{D}/nserc_raw/award_*.csv')):
        for r in rows(fn):
            aw[(r['ApplicationID'], r['FiscalYear'][:4])] = r
            aw.setdefault((r['ApplicationID'], None), r)
    hw = []; partnered = collections.Counter()
    for fn in sorted(glob.glob(f'{D}/nserc_partners_raw/partner_*.csv')):
        for r in rows(fn):
            fy = r['FiscalYear'][:4]; a = aw.get((r['ApplicationID'], fy)) or aw.get((r['ApplicationID'], None))
            inst = a['Institution'] if a else '?'
            partnered[(inst, fy)] += 1
            if 'huawei' in r['PartInstitution'].lower():
                hw.append({'app': r['ApplicationID'], 'fy': int(fy), 'partner': r['PartInstitution'], 'inst': inst,
                           'program': a.get('ProgramNameEN') if a else None, 'amount': float(a['AwardAmount'] or 0) if a else None,
                           'pi': a.get('Name') if a else None, 'title': a.get('ApplicationTitle') if a else None})
    first = {}
    for h in hw: first[h['app']] = min(first.get(h['app'], 9999), h['fy'])
    summ = {'grant_years_by_fy': dict(sorted(collections.Counter(str(h['fy']) for h in hw).items())),
            'grant_years_by_institution': dict(sorted(collections.Counter(h['inst'] for h in hw).items())),
            'grant_years_by_program': dict(sorted(collections.Counter(str(h['program']) for h in hw).items())),
            'new_applications_by_first_fy': dict(sorted(collections.Counter(str(v) for v in first.values()).items())),
            'applications': len(first),
            'note': 'Aggregated from NSERC open awards and partner files FY2012-2024 (fiscal years start 1 April). Grant-level rows (with applicant names and titles) are in NSERC open data, not republished here.'}
    json.dump(summ, open(f'{D}/nserc_huawei_summary.json', 'w'), ensure_ascii=False, indent=1)
    by = collections.defaultdict(collections.Counter); amt = collections.defaultdict(collections.Counter)
    for h in hw: by[h['inst']][h['fy']] += 1; amt[h['inst']][h['fy']] += h['amount'] or 0
    print('grant-years with Huawei partner', len(hw), 'unmatched inst', sum(h['inst'] == '?' for h in hw))
    yrs = range(2012, 2025)
    print(f"{'institution':34} " + ' '.join(f'{y%100:>3}' for y in yrs) + '   $k total')
    for inst, c in sorted(by.items(), key=lambda kv: -sum(kv[1].values())):
        print(f"{inst[:34]:34} " + ' '.join(f'{c.get(y,0):3d}' for y in yrs) + f"  {sum(amt[inst].values())/1000:8.0f}")
    print('new Huawei applications by first fiscal year:')
    first = {}
    for h in hw: first[h['app']] = min(first.get(h['app'], 9999), h['fy'])
    print(sorted(collections.Counter(first.values()).items()))
    print('programs', collections.Counter(h['program'] for h in hw).most_common(8))


if __name__ == '__main__':
    main()
