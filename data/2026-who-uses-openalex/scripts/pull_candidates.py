"""Pull every work that might use OpenAlex, from the public OpenAlex API (standard library only).

Three signals, each pulled whole (corpus=all, so repository and dataset records count too):
  fulltext   filter=fulltext.search:openalex          (the word appears in the indexed full text)
  titleabs   filter=title_and_abstract.search:openalex (the word appears in the title or abstract)
  cites      filter=cites:W4229010617                  (cites the 2022 paper that describes OpenAlex)
Raw pages go to data/raw/<signal>/page_NNN.json; a re-run skips pages already saved. data/ holds per-paper records
(author names included) and is not published.
Key: env OPENALEX_API_KEY. With a key, cursor paging (no size limit). Without one, page paging, which stops at
10,000 results; the keyless allowance (1,000 credits a day, shared by your IP) covers one run, as on 24 Nov 2026.
"""
import json, os, sys, time, urllib.parse, urllib.request

BASE = 'https://api.openalex.org/works'
SIGNALS = {
    'fulltext': 'fulltext.search:openalex',
    'titleabs': 'title_and_abstract.search:openalex',
    'cites': 'cites:W4229010617',
}
SELECT = ','.join([
    'id', 'doi', 'title', 'publication_year', 'publication_date', 'created_date', 'type', 'language',
    'authorships', 'primary_topic', 'awards', 'funders', 'abstract_inverted_index', 'best_oa_location',
    'locations', 'has_content', 'has_fulltext', 'open_access', 'cited_by_count', 'primary_location',
    'is_xpac', 'corresponding_institution_ids', 'referenced_works_count', 'is_retracted', 'is_paratext',
])
HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, '..', 'data', 'raw')


def get(params):
    key = os.environ.get('OPENALEX_API_KEY')
    if key:
        params = dict(params, api_key=key)
    url = BASE + '?' + urllib.parse.urlencode(params)
    for attempt in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'field-notes research'}), timeout=120) as r:
                return json.load(r), r.headers.get('x-ratelimit-remaining')
        except Exception as e:  # noqa: BLE001
            print('  retry', attempt, e, file=sys.stderr)
            time.sleep(5 * (attempt + 1))
    raise RuntimeError('failed: ' + url)


def pull(name, flt):
    out = os.path.join(RAW, name)
    os.makedirs(out, exist_ok=True)
    keyed = bool(os.environ.get('OPENALEX_API_KEY'))
    page, cursor, total = 1, '*', None
    while True:
        f = os.path.join(out, f'page_{page:03d}.json')
        if os.path.exists(f):
            d = json.load(open(f))
        else:
            params = {'filter': flt, 'per_page': 200, 'select': SELECT, 'corpus': 'all'}
            params.update({'cursor': cursor} if keyed else {'page': page})
            d, remaining = get(params)
            json.dump(d, open(f, 'w'))
            print(name, 'page', page, 'results', len(d['results']), 'of', d['meta']['count'], 'credits left', remaining, flush=True)
            time.sleep(0.3)
        total = d['meta']['count']
        if not keyed and total > 10000:
            sys.exit(f'{name}: {total} results; without a key, paging stops at 10,000. Set OPENALEX_API_KEY.')
        cursor = d['meta'].get('next_cursor')
        if not d['results'] or page * 200 >= total or (keyed and not cursor):
            break
        page += 1


if __name__ == '__main__':
    for name in (sys.argv[1:] or SIGNALS):
        pull(name, SIGNALS[name])
