"""Control candidates: for each treated event, 12 nearest journals in the same subfield that show no sign of ever opening content.
Pool exclusions: any source in any web-scan table (all classes/confidences), any ISSN with a delayed open licence in Crossref (Q02,
any family/version), DOAJ, is_oa, oa_flip_year not null, ever on Elsevier's open-archive list, ever on HighWire's free-back-issue
lists (title match), works < 300, first_publication_year > event cohort start + 5. Distance: log works, log(2-yr citedness + 0.1),
first publication year / 20, same country +0, else +0.25. Out: data/control_candidates.tsv"""
import csv, json, re, html, math, collections
csv.field_size_limit(10**9)
def rd(p): return list(csv.DictReader(open(p), delimiter='\t', quoting=csv.QUOTE_NONE))
def norm(s): s = html.unescape(s or '').lower().replace('&', 'and'); return re.sub(r'[^a-z0-9]+', ' ', s).strip()
src = json.load(open('data/q03_sources.json')); cols = src['cols']
S = {}; iss2src = {}; name2sid = collections.defaultdict(set)
for r in src['rows']:
    s = dict(zip(cols, r)); S[s['id']] = s; name2sid[norm(s['display_name'])].add(s['id'])
    for i in json.loads(s['issn'] or '[]') + [s['issn_l']]:
        if i: iss2src.setdefault(i.upper(), s['id'])
bad = set()
for p in ('A_datasets_events', 'B_programs_events', 'C_announcements_events'):
    for r in rd(f'results/web_scan/{p}.tsv'):
        for i in re.split(r'[;,\s]+', r['issn'] or ''):
            if i.upper() in iss2src: bad.add(iss2src[i.upper()])
        bad |= name2sid.get(norm(r['journal_title']), set())
for r in json.load(open('data/q02.json'))['rows']:
    if r[0] and r[0].upper() in iss2src: bad.add(iss2src[r[0].upper()])
for r in rd('data/elsevier_archive_lists.tsv'): bad |= name2sid.get(norm(r['journal']), set())
for r in rd('data/web_scan/datasets/highwire_freeart_wayback/highwire_journal_timeline.tsv'): bad |= name2sid.get(norm(r['title']), set())
pool = [s for sid, s in S.items() if sid not in bad and s['is_in_doaj'] != 'true' and s['is_oa'] != 'true'
        and s['oa_flip_year'] in (None, 'None') and int(s['works_count']) >= 300 and s['first_publication_year'] not in (None, 'None')]
print('excluded by any opening signal', len(bad), '; clean pool', len(pool))
by_sub = collections.defaultdict(list)
for s in pool: by_sub[s['subfield']].append(s)
def f(x, d=0.0):
    try: return float(x)
    except: return d
out = []; thin = 0
for e in rd('results/final_events.tsv'):
    t = S.get(e['source'])
    if not t: continue
    cand = [s for s in by_sub[t['subfield']] if int(s['first_publication_year']) <= int(e['cohort_from']) + 5 or int(s['first_publication_year']) <= int(e['cohort_to']) - 5]
    def dist(s):
        return (abs(math.log(f(s['works_count'], 1)) - math.log(f(t['works_count'], 1))) + abs(math.log(f(s['c2']) + .1) - math.log(f(t['c2']) + .1))
                + abs(int(s['first_publication_year']) - int(t['first_publication_year'])) / 20 + (0 if s['country_code'] == t['country_code'] else .25))
    cand.sort(key=dist)
    if len(cand) < 5: thin += 1
    for rank, s in enumerate(cand[:12]):
        out.append(dict(treated=e['source'], T=e['T'], cohort_from=e['cohort_from'], cohort_to=e['cohort_to'], control=s['id'],
                        control_name=' '.join((s['display_name'] or '').split()), rank=rank, dist=round(dist(s), 3), subfield=t['subfield']))
with open('data/control_candidates.tsv', 'w') as fh:
    ks = list(out[0]); fh.write('\t'.join(ks) + '\n')
    for x in out: fh.write('\t'.join(str(x[k]) for k in ks) + '\n')
ids = {x['control'] for x in out} | {x['treated'] for x in out}
open('data/panel_source_ids.txt', 'w').write('\n'.join(sorted(ids)))
print('events with candidates', len({x['treated'] for x in out}), '; events with < 5 candidates', thin, '; distinct controls', len({x['control'] for x in out}), '; panel sources', len(ids))
