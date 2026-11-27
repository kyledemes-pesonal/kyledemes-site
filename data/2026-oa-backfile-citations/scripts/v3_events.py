"""v3 cohort fixes (22 Nov 2026). Reads results/final_events.tsv (v1, untouched) and data/elsevier_joiners.tsv; writes
results/v3/final_events_v3.tsv with the v3 cohort bounds and a v3 status per event:
  pure / annual_reviews / other_flip (v2 groups, unchanged unless listed below) / front_list (moved out of pure: the journal's
  new papers also changed at T) / dropped (not in any v3 set).
Fix 1: Elsevier open-archive joiners: cohort lower bound = the list's back_to (data/elsevier_joiners.tsv; the open archive is
  dated per journal), not 1900. Virology's list says 2013 (= T), contradicted by Crossref licences and OpenAlex today
  (1995 onward open): 1995. A joiner whose back_to falls after its cohort end opened nothing at T: dropped.
Fix 2/4: openings that did not hold through the post window: dropped (Bell System Technical Journal: free archive last
  captured live Nov 2014, URLs redirect from 2015, now IEEE Xplore paid; Significance: RSS journals moved to OUP, 2004-2013
  volumes paywalled today; Canadian Association of Radiologists Journal: moved to SAGE, archive closed today).
  Front-list changes and first digitization moved out of pure: J Economic Perspectives (2010), Internet Archaeology (2012),
  Progress of Theoretical Physics and its Supplement (PTP to PTEP 2013), Journal of Hygiene (PMC first digitization).
Fix 3 (records without the journal's DOI prefix) is applied to the panel in v3_common.py, not here."""
import csv, os, collections
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def rd(p): return list(csv.DictReader(open(p), delimiter='\t', quoting=csv.QUOTE_NONE))
ev = rd('results/final_events.tsv')
jn = {r['source']: r for r in rd('data/elsevier_joiners.tsv') if r['source']}
BACK_TO_OVERRIDE = {'6147291': (1995, "list back_to 2013 contradicted by Crossref licences and OpenAlex (1995 onward open)")}
DROP = {'127472826': 'opening did not hold: free BSTJ archive (alcatel-lucent.com/bstj) last captured live Nov 2014, redirects from 2015, now IEEE Xplore (paid)',
        '151374650': 'opening did not hold: RSS journals moved to OUP; 2004-2013 volumes paywalled today (checked 22 Nov 2026)',
        '2754793730': 'opening did not hold: journal moved to SAGE; Elsevier-era archive closed today (98% closed in OpenAlex)'}
FRONT = {'Economic Perspectives': 'front list also opened at T (methods check)', 'Internet Archaeology': 'front list also opened at T (methods check)',
         'Progress of Theoretical Physics': 'PTP to PTEP transition: new OA journal at T (methods check)',
         'Journal of Hygiene': 'date is PMC first digitization, not a paywall removal (methods check)'}
AR = ('Annual Reviews S2O 2023 (previous nine volumes)', 'Annual Reviews S2O pilot (all back volumes)')
out = []
for e in ev:
    e = dict(e); e['v1_cohort_from'] = e['cohort_from']; reason = ''
    st = 'annual_reviews' if e['program'] in AR else ('other_flip' if e['program'] == 'single-journal opening (flip)' else 'pure')
    if 'platform move' in e['note']: st, reason = 'platform_move', 'platform move at T (v2)'
    if e['program'] == 'Elsevier open archive join':
        j = jn[e['source']]
        if e['source'] in BACK_TO_OVERRIDE: lo, why = BACK_TO_OVERRIDE[e['source']]
        else: lo, why = int(j['back_to']) if j['back_to'] else 1995, f"Elsevier list back_to {j['back_to'] or 'missing -> 1995'}"
        e['cohort_from'] = str(lo); reason = why
        if lo > int(e['cohort_to']): st, reason = 'dropped', f"Elsevier list back_to {lo} after cohort end {e['cohort_to']}: nothing in the back file opened at T"
    if e['source'] in DROP: st, reason = 'dropped', DROP[e['source']]
    hit = [k for k in FRONT if k in e['journal']]
    if hit and st == 'pure': st, reason = 'front_list', FRONT[hit[0]]
    e['v3_status'] = st; e['v3_reason'] = reason
    out.append(e)
ks = list(out[0])
with open('results/v3/final_events_v3.tsv', 'w') as fh:
    fh.write('\t'.join(ks) + '\n')
    for x in out: fh.write('\t'.join(str(x[k]) for k in ks) + '\n')
c = collections.Counter(x['v3_status'] for x in out); print(c)
for x in out:
    if x['v3_status'] in ('dropped', 'front_list') or x['program'] == 'Elsevier open archive join':
        print(f"{x['v3_status']:12s} {x['journal'][:45]:45s} T={x['T']} {x['v1_cohort_from']}->{x['cohort_from']}-{x['cohort_to']} | {x['v3_reason'][:80]}")
