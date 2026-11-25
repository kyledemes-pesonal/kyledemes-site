"""Denominators: all research papers published 2022-2026, and those with full text in OpenAlex, by country, field,
funder and year (group_by queries on the public API, 1 credit each), plus the count of papers with at least one
author country. Output: results/denominators.json (a re-run keeps entries already saved)."""
import json, os, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
TYPES = 'article|review|preprint|conference-paper|book-chapter|book|dissertation|report'
BASE = f'publication_year:2022-2026,type:{TYPES}'
QUERIES = {
    'country_all': (BASE, 'authorships.countries'),
    'country_ft': (BASE + ',has_fulltext:true', 'authorships.countries'),
    'field_all': (BASE, 'primary_topic.field.id'),
    'field_ft': (BASE + ',has_fulltext:true', 'primary_topic.field.id'),
    'year_all': (BASE, 'publication_year'),
    'year_ft': (BASE + ',has_fulltext:true', 'publication_year'),
    'funder_all': (BASE, 'funders.id'),
    'funder_ft': (BASE + ',has_fulltext:true', 'funders.id'),
    'with_country_all': (BASE + ',countries_distinct_count:>0', None),  # papers with at least one author country
}


def get(params):
    key = os.environ.get('OPENALEX_API_KEY')
    if key:
        params = dict(params, api_key=key)
    url = 'https://api.openalex.org/works?' + urllib.parse.urlencode(params)
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'field-notes research'}), timeout=120) as r:
        return json.load(r)


if __name__ == '__main__':
    path = os.path.join(HERE, '..', 'results', 'denominators.json')
    out = json.load(open(path)) if os.path.exists(path) else {}
    for name, (flt, gb) in QUERIES.items():
        if name in out:
            continue
        q = {'filter': flt, 'per_page': 200 if gb else 1, 'corpus': 'all'}
        if gb:
            q['group_by'] = gb
        d = get(q)
        out[name] = {'filter': flt, 'group_by': gb, 'count': d['meta']['count'], 'pulled': time.strftime('%Y-%m-%d'),
                     'groups': [{'key': g['key'], 'name': g['key_display_name'], 'count': g['count']} for g in d.get('group_by') or []]}
        print(name, d['meta']['count'], len(out[name]['groups']))
        json.dump(out, open(path, 'w'), indent=1)
