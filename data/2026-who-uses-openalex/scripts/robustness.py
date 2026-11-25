"""Numbers in the post that test or extend the headline counts. Reads data/ and results/ (run after analyse.py).
Output: results/robustness.json (aggregates only; author IDs are used inside the prolific-author check, never saved).
- cites_by_year: of papers that used OpenAlex and have a reference list in OpenAlex, the share citing W4229010617
- reviews: papers whose use was finding studies for a review, 2025 and 2026
- prolific: 2026 vs 2025 after dropping papers with any author on 5+ of that year's papers
- estimate: the 7,500 to 9,000 range for papers that used OpenAlex, with its two assumptions
- fulltext_share: share of all research papers 2022-2026 with full text in OpenAlex
"""
import collections, csv, glob, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA, RES = os.path.join(HERE, '..', 'data'), os.path.join(HERE, '..', 'results')
PAPER_TYPES = {'article', 'review', 'preprint', 'conference-paper', 'book-chapter', 'book', 'dissertation', 'report'}
USED = {'data_source', 'subject', 'tool'}

recs, sets = {}, {}
for s in ('cites', 'titleabs', 'fulltext'):
    ids = set()
    for f in glob.glob(os.path.join(DATA, 'raw', s, 'page_*.json')):
        for w in json.load(open(f))['results']:
            ids.add(w['id'])
            recs[w['id']] = w
    sets[s] = ids
labels = {}
for fn in ('labels.jsonl', 'labels_late_abstract.jsonl'):
    for l in open(os.path.join(DATA, fn)):
        r = json.loads(l)
        labels[r['work']] = r
pas = {}
for l in open(os.path.join(DATA, 'passages.jsonl')):
    r = json.loads(l)
    pas[r['id']] = r
corpus = list(csv.DictReader(open(os.path.join(RES, 'corpus.csv'))))
W = {r['work_id']: recs['https://openalex.org/' + r['work_id']] for r in corpus}
out = {}

# 1. citing the OpenAlex paper, by year
cy = {}
for y in sorted({r['publication_year'] for r in corpus}):
    sub = [r for r in corpus if r['publication_year'] == y and (W[r['work_id']].get('referenced_works_count') or 0) > 0]
    c = sum(W[r['work_id']]['id'] in sets['cites'] for r in sub)
    cy[y] = {'with_references': len(sub), 'cite': c, 'share': round(c / len(sub), 3) if sub else None}
out['cites_by_year'] = cy

# 2. reviews
yc = collections.Counter((r['publication_year'], r['use'] == 'literature_search') for r in corpus)
out['reviews'] = {y: {'reviews': yc[(y, True)], 'papers': yc[(y, True)] + yc[(y, False)]} for y in ('2025', '2026')}

# 3. prolific authors
per = {}
for y in ('2025', '2026'):
    rows = [r for r in corpus if r['publication_year'] == y]
    n = collections.Counter(a['author']['id'] for r in rows for a in W[r['work_id']].get('authorships') or [] if (a.get('author') or {}).get('id'))
    keep = [r for r in rows if all(n[a['author']['id']] < 5 for a in W[r['work_id']].get('authorships') or [] if (a.get('author') or {}).get('id'))]
    per[y] = {'papers': len(rows), 'without_prolific': len(keep)}
out['prolific'] = dict(per, ratio_all=round(per['2026']['papers'] / per['2025']['papers'], 2),
                       ratio_without_prolific=round(per['2026']['without_prolific'] / per['2025']['without_prolific'], 2))

# 4. the estimate
def is_paper(w):
    return w.get('type') in PAPER_TYPES and (w.get('publication_year') or 0) in range(2022, 2027)
body = [i for i in (sets['fulltext'] | sets['cites']) - sets['titleabs'] if is_paper(recs[i])]
read = [i for i in body if pas.get(i, {}).get('status') == 'ok']
unread = [i for i in body if pas.get(i, {}).get('status') != 'ok']
rate = sum(labels[i]['role'] in USED for i in read) / len(read)
ta = [r for r in corpus if r['how_found'] == 'title_abstract']
found_body = sum(r['how_found'] != 'title_abstract' for r in corpus)
f_users = sum(bool(W[r['work_id']].get('has_fulltext')) for r in ta) / len(ta)
den = json.load(open(os.path.join(RES, 'denominators.json')))
f_all = den['year_ft']['count'] / den['year_all']['count']
body_total = found_body + len(unread) * rate
out['estimate'] = {
    'floor': len(corpus), 'found_title_abstract': len(ta), 'found_body': found_body,
    'body_papers_read': len(read), 'body_papers_unread': len(unread), 'use_rate_read_body': round(rate, 3),
    'fulltext_share_title_abstract_users': round(f_users, 3), 'fulltext_share_all_papers': round(f_all, 3),
    'estimate_with_user_share': round(len(ta) + body_total / f_users),
    'estimate_with_all_paper_share': round(len(ta) + body_total / f_all),
    'assumptions': 'papers I could not read used OpenAlex as often as those I could; papers without full text in '
                   'OpenAlex name it only in the body as often as those with it'}
out['fulltext_share'] = {'with_fulltext': den['year_ft']['count'], 'all': den['year_all']['count'], 'share': round(f_all, 3)}
json.dump(out, open(os.path.join(RES, 'robustness.json'), 'w'), indent=1)
print(json.dumps(out, indent=1))
