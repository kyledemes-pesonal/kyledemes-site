"""Final treated events for the main estimate (paywall removed from already-published content; JSTOR EJC separate).
Every inclusion and exclusion is written with its reason to results/final_events.tsv and results/final_exclusions.tsv.
Cohort = publication years whose articles were fully opened on date T (later cohorts that open on a rolling wall are not treated).
Rules (applied in order):
 R1 program rules (cohort ranges from the opening announcement): Elsevier maths 2012 (<=2008), Cell Press 2005-01 (1995-2003),
    Royal Society 2011-10 (<= content range end, i.e. older than 70 years), AMS 2010 (<=2005), Annual Reviews (all back volumes for
    2017 and 2020-21 pilots; the previous nine volumes for 2023 joiners), single-journal announcements with an exact range.
 R2 exclude: T >= 2025 (no full post year; citing year 2026 incomplete); first-online digitizations (JCB, JEM, Wellcome/PMC
    backfiles, J Anatomy, Medical History); PNAS (several overlapping openings 2000-2005); CMAJ and JCI (freed only non-research
    items); journals with a moving wall on HighWire before T (the flip freed only the last 12-24 months: OUP flips, AAS, RAS,
    Érudit, Biographical Memoirs); OAD-only year dates without a second source; unverified rows (Index on Censorship);
    non-scholarly or artefact rows (NAR, patent reports); JSTOR EJC and the Royal Geographical Society rows (reported separately).
 R3 Elsevier open-archive joiners 2013-2020 dated by Wayback captures of Elsevier's list (+ Crossref licence start when it falls in
    the window), only Elsevier-native journals (>= 80% of works in the 5 years before T carry a 10.1016 DOI), cohort = publication
    years older than the embargo at T.
"""
import csv, json, math, collections, re, html
csv.field_size_limit(10**9)
def rd(p): return list(csv.DictReader(open(p), delimiter='\t', quoting=csv.QUOTE_NONE))
ev = [x for x in rd('results/merged_events_sized.tsv') if x['cls'] == 'PW']
inc, exc = [], []
def add(x, T, lo, hi, prog, tier_src, note=''):
    inc.append(dict(source=x['source'], journal=x['journal'], program=prog, T=T, cohort_from=lo, cohort_to=hi,
                    n_date_sources=tier_src, flip=int('flip' in prog.lower() or 'OA' in prog), note=note))
def drop(x, why): exc.append(dict(source=x['source'], journal=x['journal'], date=x['date'], program=x['programs'][:60], reason=why))
# HighWire prior-wall check
def norm(s): s = html.unescape(s or '').lower().replace('&', 'and'); return re.sub(r'[^a-z0-9]+', ' ', s).strip()
hw = {}
for r in rd('data/web_scan/datasets/highwire_freeart_wayback/highwire_journal_timeline.tsv'):
    walls = [k.split(':')[0] for k in (r['wall_history'] or '').split(' | ') if k] + [k.split(':')[0] for k in (r['range_history'] or '').split(' | ') if k]
    if walls: hw[norm(r['title'])] = min(walls)
for x in ev:
    j, p, d, c = x['journal'], x['programs'], x['date'], x['content']
    T = int(d[:4]); fy = int(x['first_year'] or 0)
    if 'Early Journal Content' in p or 'Royal Geographical' in j: drop(x, 'JSTOR EJC: reported separately'); continue
    if T >= 2025: drop(x, 'T >= 2025: no full post year'); continue
    if any(k in j for k in ('Cell Biology', 'Experimental Medicine', 'Physiology', 'Biochemical Journal', 'Journal of Anatomy', 'Medical History')) and ('RUP' in p or 'Wellcome' in p or 'JCB' in p or 'Anatomy' in p):
        drop(x, 'first-online digitization, not a paywall removal'); continue
    if 'National Academy' in j: drop(x, 'PNAS: several overlapping openings 2000-2005'); continue
    if 'Canadian Medical' in j or 'Clinical Investigation' in j: drop(x, 'freed only non-research items'); continue
    if 'Index on Censorship' in j: drop(x, 'source page not verified'); continue
    if 'Nucleic Acids' in j or 'Patent' in j: drop(x, 'artefact / non-scholarly'); continue
    if 'Epidemiology and Infection' in j: drop(x, 'opened range unknown (source merges J Hygiene)'); continue
    if 'Interdisciplinary CardioVascular' in j or 'International Health' in j: drop(x, 'OUP flip, prior moving wall likely, range unclear'); continue
    hwd = hw.get(norm(j))
    if hwd and hwd < d and 'Elsevier' not in p and 'Cell Press' not in p and 'Royal Society' not in p:
        drop(x, f'moving wall on HighWire since {hwd}: flip freed only recent content'); continue
    if any(k in p for k in ('AAS journals', 'RAS journals', 'Érudit', 'Royal Society policy change')):
        drop(x, 'prior moving wall (12-36 months): flip freed only recent content'); continue
    if 'Open Access Directory' in p and int(x['n_date_sources']) < 2: drop(x, 'OAD year-only date without a second source'); continue
    nds = int(x['n_date_sources'])
    if 'Elsevier open archive: primary math' in p:
        m = re.search(r'issues (\d{4})-(\d{4})', c)
        lo = int(m.group(1)) if m else fy; hi = 2008 if 'pre-1995' not in c else (int(m.group(2)) if m else 1994)
        add(x, 2012, min(lo, fy) if 'pre-1995' in c else fy, hi, 'Elsevier maths open archive 2012', nds, 'pre-1995 back file opened 2012-09, 1995-2008 in 2012-05'); continue
    if 'Cell Press' in p:
        if T != 2005: drop(x, 'Cell Press title launched later (opens on rolling wall)'); continue
        add(x, 2005, max(fy, 1995), 2003, 'Cell Press archive 2005', nds); continue
    if 'Royal Society historical' in p:
        m = re.search(r'issues (\d{4})-(\d{4})', c); add(x, 2011, int(m.group(1)) if m else fy, int(m.group(2)) if m else 1941, 'Royal Society archive 2011', nds); continue
    if 'AMS journal' in p: add(x, 2010, fy, 2005, 'AMS back file 2010', nds, 'month uncertain (May-Aug 2010)'); continue
    if 'Annual Reviews' in p:
        if 'nine volumes' in c:
            m = re.search(r'about (\d{4})-(\d{4})', c); add(x, T, int(m.group(1)) if m else T - 9, T - 1, 'Annual Reviews S2O 2023 (previous nine volumes)', nds); continue
        m = re.search(r'from (\d{4}) to (\d{4})', c)
        add(x, T, int(m.group(1)) if m else fy, T - 1, 'Annual Reviews S2O pilot (all back volumes)', nds); continue
    ranges = {'International Journal of Surgery': (2003, 2012), 'Progress of Theoretical Physics': (fy, 2012),
              'Journal of Hygiene': (fy, 1986), 'Journal of Biomedical Optics': (1996, 2018), 'Neurophotonics': (2014, 2018),
              'Bell System Technical Journal': (1922, 1983), 'Genetics Selection Evolution': (fy, 2008), 'Zygon': (1966, 2023),
              'IDS Bulletin': (fy, 2015), 'Economic Perspectives': (1999, 2009), 'Geographica Helvetica': (fy, 2011),
              'Acta Mathematica': (fy, 2016), 'Significance': (2004, 2013), 'Daedalus': (2003, 2020),
              'Internet Archaeology': (2001, 2011), 'Green Chemistry Letters': (2007, 2007), 'Annual Review of Public Health': (1980, 2016)}
    hit = [k for k in ranges if k in j]
    if hit:
        lo, hi = ranges[hit[0]]
        flag = 'platform move at T' if any(k in j for k in ('Zygon', 'Acta Mathematica', 'Genetics Selection', 'Geographica', 'IDS Bulletin')) else ''
        add(x, T, lo, hi, 'single-journal opening' + (' (flip)' if 'flip' in p.lower() or 'OA' in p else ''), nds, flag); continue
    drop(x, 'no rule: range or prior access unclear')
# R3 Elsevier joiners
q7 = json.load(open('data/q07.json'))['rows']
pre = collections.defaultdict(dict)
for sid, y, n, n1016 in q7:
    if y is not None: pre[str(sid)][int(y)] = (int(n), int(n1016))
have = {e['source'] for e in inc}
for j in rd('data/elsevier_joiners.tsv'):
    x = dict(source=j['source'], journal=j['journal'], date=j['first_seen'], programs='Elsevier open archive join (Wayback)')
    if not j['source']: drop(x, 'joiner: title not uniquely mapped'); continue
    if j['source'] in have: drop(x, 'joiner: already an R1 event'); continue
    a = int(j['last_not_seen'][:4]) * 12 + int(j['last_not_seen'][4:6]) - 1; b = int(j['first_seen'][:4]) * 12 + int(j['first_seen'][4:6]) - 1
    lt = j['licence_T']
    if lt and a - 1 <= int(lt[:4]) * 12 + int(lt[5:7]) - 1 <= b + 1 and lt != '2013-07-01':
        tm = int(lt[:4]) * 12 + int(lt[5:7]) - 1; nds = 2
    elif b - a <= 12:
        tm = (a + b) // 2; nds = 1
    else:
        drop(x, f'joiner: Wayback window {j["last_not_seen"]}-{j["first_seen"]} > 12 months and no licence date inside it'); continue
    T = tm // 12
    if T >= 2025: drop(x, 'T >= 2025'); continue
    yrs = [pre[j['source']].get(y, (0, 0)) for y in range(T - 5, T)]
    n, n1 = sum(v[0] for v in yrs), sum(v[1] for v in yrs)
    if n < 50 or n1 / n < 0.8: drop(x, f'joiner: not Elsevier-native before T (10.1016 share {n1/max(n,1):.2f}); transferred journals may have been free at the old host'); continue
    emb = int(j['embargo_months'] or 12)
    hi = T - math.ceil(emb / 12) - 1
    x2 = dict(source=j['source'], journal=j['journal'])
    add(x2, T, 0, hi, 'Elsevier open archive join', nds, f'embargo {emb} months; window {j["last_not_seen"]}-{j["first_seen"]}')
for e in inc:
    if e['cohort_from'] in (0, None): e['cohort_from'] = 1900
for p, rows in (('results/final_events.tsv', inc), ('results/final_exclusions.tsv', exc)):
    with open(p, 'w') as fh:
        ks = list(rows[0]); fh.write('\t'.join(ks) + '\n')
        for x in rows: fh.write('\t'.join(' '.join(str(x[k]).split()) for k in ks) + '\n')
print('included', len(inc), 'events /', len({e['source'] for e in inc}), 'journals; excluded', len(exc))
print(collections.Counter(e['program'] for e in inc).most_common())
print(collections.Counter(e['reason'].split(':')[0][:60] for e in exc).most_common())
print('>=2 date sources:', sum(1 for e in inc if int(e['n_date_sources']) >= 2))
