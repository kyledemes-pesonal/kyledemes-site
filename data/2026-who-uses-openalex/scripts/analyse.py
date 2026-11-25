"""Build the corpus of research papers that used OpenAlex and tabulate it. Output: results/*.json, results/corpus.csv.

Corpus rule: a candidate (full text, title or abstract says "OpenAlex", or it cites W4229010617) whose label is
data_source, subject or tool; published 2022-2026; a research-paper type; preprint/published twins collapsed by
normalised title (the later-published, non-preprint record kept). Countries, institutions, funders: full counting
(a paper counts once for each distinct country / institution / funder on it).
"""
import collections, csv, glob, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
DATA, RES = os.path.join(HERE, '..', 'data'), os.path.join(HERE, '..', 'results')
USED = {'data_source', 'subject', 'tool'}
PAPER_TYPES = {'article', 'review', 'preprint', 'conference-paper', 'book-chapter', 'book', 'dissertation', 'report'}


def load():
    recs, sets = {}, {}
    for s in ('cites', 'titleabs', 'fulltext'):
        ids = set()
        for f in glob.glob(os.path.join(DATA, 'raw', s, 'page_*.json')):
            for w in json.load(open(f))['results']:
                ids.add(w['id'])
                recs[w['id']] = w
        sets[s] = ids
    labels = {}
    # labels_late_abstract.jsonl: relabels of works whose abstract names OpenAlex after the 1,800-character cut
    for fn in ('labels.jsonl', 'labels_late_abstract.jsonl'):
        if os.path.exists(os.path.join(DATA, fn)):
            for l in open(os.path.join(DATA, fn)):
                r = json.loads(l)
                labels[r['work']] = r
    pas = {json.loads(l)['id']: json.loads(l) for l in open(os.path.join(DATA, 'passages.jsonl'))} \
        if os.path.exists(os.path.join(DATA, 'passages.jsonl')) else {}
    return recs, sets, labels, pas


def norm(t):
    return re.sub(r'[^a-z0-9]+', ' ', (t or '').lower()).strip()[:150]


def group(w, sets, pas):
    if w['id'] in sets['titleabs']:
        return 'title_abstract'
    p = pas.get(w['id'])
    return 'body_read' if p and p.get('status') == 'ok' else 'body_unread'


def main():
    recs, sets, labels, pas = load()
    allc = sorted(set(recs))
    out = {}
    # 1. funnel: every candidate and its label
    fun = collections.Counter()
    for i in allc:
        g = group(recs[i], sets, pas)
        role = labels.get(i, {}).get('role') or 'not_labelled'
        # "not about OpenAlex" only counts as a judgement when the model could see the word
        if role == 'false_positive':
            ab = ' '.join(w for _, w in sorted((k, w) for w, ks in (recs[i].get('abstract_inverted_index') or {}).items() for k in ks))
            seen = bool(re.search(r'open ?alex', (recs[i].get('title') or '') + ' ' + ab, re.I)) if g == 'title_abstract' \
                else (pas.get(i, {}).get('n_mentions', 0) > 0)
            if not seen:
                role = 'unclear'
        fun[(g, role)] += 1
    out['funnel'] = [{'group': g, 'role': r, 'works': n} for (g, r), n in sorted(fun.items())]

    # 2. corpus
    # W4229010617 is the paper that describes OpenAlex itself, not a use of it
    used = [recs[i] for i in allc if labels.get(i, {}).get('role') in USED and i != 'https://openalex.org/W4229010617']
    papers = [w for w in used if w.get('type') in PAPER_TYPES and (w.get('publication_year') or 0) in range(2022, 2027)]
    others = collections.Counter(w.get('type') for w in used if w.get('type') not in PAPER_TYPES)
    by_title = {}
    for w in papers:
        k = norm(w.get('title'))
        if not k or len(k) < 20:
            k = w['id']
        keep = by_title.get(k)
        rank = lambda x: (x.get('type') != 'preprint', x.get('publication_date') or '')
        if keep is None or rank(w) > rank(keep):
            by_title[k] = w
    corpus = list(by_title.values())
    out['corpus_size'] = {'used_any_type': len(used), 'papers_before_dedupe': len(papers), 'papers': len(corpus),
                          'non_paper_used_by_type': dict(others.most_common())}

    # 3. roles, uses, years, types
    out['roles'] = dict(collections.Counter(labels[w['id']]['role'] for w in corpus))
    out['uses'] = dict(collections.Counter(labels[w['id']].get('use') or 'none' for w in corpus).most_common())
    out['years'] = dict(sorted(collections.Counter(w['publication_year'] for w in corpus).items()))
    out['years_by_group'] = {g: dict(sorted(collections.Counter(w['publication_year'] for w in corpus
                                                                if group(w, sets, pas) == g).items()))
                             for g in ('title_abstract', 'body_read', 'body_unread')}
    out['types'] = dict(collections.Counter(w['type'] for w in corpus).most_common())

    # 4. countries, institutions, fields, funders (full counting)
    cty, inst, inst_name, inst_cty, fld, fnd, fnd_name = (collections.Counter(), collections.Counter(), {}, {},
                                                          collections.Counter(), collections.Counter(), {})
    no_cty = no_fnd = 0
    for w in corpus:
        cs = {c for a in w.get('authorships') or [] for c in (a.get('countries') or [])}
        no_cty += not cs
        cty.update(cs)
        ins = {}
        for a in w.get('authorships') or []:
            for x in a.get('institutions') or []:
                ins[x['id']] = x
        for k, x in ins.items():
            inst[k] += 1
            inst_name[k] = x.get('display_name')
            inst_cty[k] = x.get('country_code')
        f = (w.get('primary_topic') or {}).get('field') or {}
        fld[f.get('display_name') or 'Unknown'] += 1
        fs = {x['id']: x.get('display_name') for x in w.get('funders') or []}
        no_fnd += not fs
        fnd.update(fs.keys())
        fnd_name.update(fs)
    n = len(corpus)
    den = json.load(open(os.path.join(RES, 'denominators.json')))

    def dmap(k):
        return {g['key'].split('/')[-1]: g['count'] for g in den[k]['groups']}
    call, cft = dmap('country_all'), dmap('country_ft')
    n_cty = n - no_cty  # papers with at least one author country
    all_cty = den['with_country_all']['count']
    out['countries'] = [{'country': c, 'papers': k, 'share_of_corpus': round(k / n, 6),
                         'share_of_corpus_with_country': round(k / n_cty, 6),
                         'share_of_all_papers_with_country': round(call.get(c, 0) / all_cty, 6),
                         'all_papers_2022_2026': call.get(c), 'fulltext_papers_2022_2026': cft.get(c),
                         'per_10k_papers': round(k / call[c] * 1e4, 2) if call.get(c) else None,
                         'per_10k_fulltext_papers': round(k / cft[c] * 1e4, 2) if cft.get(c) else None}
                        for c, k in cty.most_common(60)]
    out['countries_meta'] = {'papers_with_no_country': no_cty, 'distinct_countries': len(cty),
                             'denominator_total_all': den['country_all']['count'],
                             'denominator_total_ft': den['country_ft']['count']}
    out['institutions'] = [{'id': k.split('/')[-1], 'name': inst_name[k], 'country': inst_cty[k], 'papers': v}
                           for k, v in inst.most_common(60)]
    out['countries_meta']['papers_with_country'] = n - no_cty
    fall = {g['name']: g['count'] for g in den['field_all']['groups']}
    fft = {g['name']: g['count'] for g in den['field_ft']['groups']}
    tall, tft = sum(fall.values()), sum(fft.values())
    n_fld = n - fld.get('Unknown', 0)
    out['fields'] = [{'field': f, 'papers': k, 'share_of_corpus': round(k / n_fld, 6),
                      'share_of_all_papers': round(fall.get(f, 0) / tall, 6),
                      'share_of_fulltext_papers': round(fft.get(f, 0) / tft, 6)} for f, k in fld.most_common()]
    fda = {g['key'].split('/')[-1]: g['count'] for g in den['funder_all']['groups']}
    out['funders'] = [{'id': k.split('/')[-1], 'name': fnd_name[k], 'papers': v,
                       'share_of_corpus': round(v / n, 6),
                       'all_papers_2022_2026': fda.get(k.split('/')[-1])} for k, v in fnd.most_common(60)]
    # the EU's programmes appear as separate funders; count papers with any of them once
    eu = re.compile(r'european commission|horizon (europe|2020)|h2020|european research council|nextgenerationeu|'
                    r'seventh framework|european regional development|erasmus|marie (sk|curie)|european union', re.I)
    fam = collections.Counter()
    for w in corpus:
        names = {x.get('display_name') or '' for x in w.get('funders') or []}
        keys = {('European Union (Commission, Horizon, ERC and other programmes)' if eu.search(nm) else nm) for nm in names}
        fam.update(keys)
    out['funders_grouped'] = [{'name': k, 'papers': v} for k, v in fam.most_common(30)]
    out['funders_meta'] = {'papers_with_any_funder': n - no_fnd, 'share_with_any_funder': round((n - no_fnd) / n, 6),
                           'distinct_funders': len(fnd)}
    # who pays: paying institutions by country (public supporters page, aggregates) vs share of using papers
    sup = json.load(open(os.path.join(RES, 'supporters.json')))  # from supporters_summary.py
    resolved = sup['total'] - sup['unresolved_country']
    sc = sup['by_country']
    codes = sorted(set(sc) | {c for c, _ in cty.most_common(15)}, key=lambda c: -(cty.get(c, 0)))
    out['pays_vs_uses'] = [{'country': c, 'share_of_using_papers': round(cty.get(c, 0) / (n - no_cty), 4),
                            'paying_institutions': sc.get(c, 0), 'share_of_paying_institutions': round(sc.get(c, 0) / resolved, 6)}
                           for c in codes]
    out['pays_meta'] = {'supporters_total': sup['total'], 'resolved': resolved, 'pulled': sup['pulled'], 'url': sup['url']}
    # citations: of papers that used OpenAlex, how many cite the OpenAlex paper (among those with references in OpenAlex)
    withrefs = [w for w in corpus if (w.get('referenced_works_count') or 0) > 0]
    out['cites_openalex_paper'] = {'papers': n, 'cite': sum(w['id'] in sets['cites'] for w in corpus),
                                   'with_references': len(withrefs),
                                   'cite_among_with_references': sum(w['id'] in sets['cites'] for w in withrefs)}
    out['institutions_meta'] = {'distinct_institutions': len(inst)}
    json.dump(out, open(os.path.join(RES, 'summary.json'), 'w'), indent=1, ensure_ascii=False)
    with open(os.path.join(RES, 'corpus.csv'), 'w', newline='') as f:
        wr = csv.writer(f)
        wr.writerow(['work_id', 'doi', 'title', 'type', 'publication_year', 'how_found', 'role', 'use', 'evidence',
                     'countries', 'field', 'funders'])
        for w in sorted(corpus, key=lambda x: x['id']):
            lb = labels[w['id']]
            wr.writerow([w['id'].split('/')[-1], w.get('doi') or '', w.get('title') or '', w['type'],
                         w['publication_year'], group(w, sets, pas), lb['role'], lb.get('use') or '',
                         lb.get('evidence') or '',
                         ';'.join(sorted({c for a in w.get('authorships') or [] for c in (a.get('countries') or [])})),
                         ((w.get('primary_topic') or {}).get('field') or {}).get('display_name') or '',
                         ';'.join(x.get('display_name') or '' for x in w.get('funders') or [])])
    print(json.dumps({k: out[k] for k in ('corpus_size', 'roles', 'uses', 'years', 'years_by_group', 'types',
                                           'countries_meta', 'funders_meta', 'cites_openalex_paper', 'institutions_meta')}, indent=1))
    print('pays', [(r['country'], r['share_of_using_papers'], r['paying_institutions']) for r in out['pays_vs_uses'][:20]])
    print('countries', [(c['country'], c['papers'], c['per_10k_papers'], c['per_10k_fulltext_papers']) for c in out['countries'][:20]])
    print('institutions', [(c['name'], c['country'], c['papers']) for c in out['institutions'][:20]])
    print('fields', [(c['field'], c['papers'], c['share_of_corpus'], c['share_of_all_papers'], c['share_of_fulltext_papers']) for c in out['fields']])
    print('funders', [(c['name'], c['papers'], c['all_papers_2022_2026']) for c in out['funders'][:25]])
    print('funnel', out['funnel'])


if __name__ == '__main__':
    main()
