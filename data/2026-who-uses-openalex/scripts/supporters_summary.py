"""Paying members of OpenAlex, counted by country, type and tier. Input: data/_private/supporters_countries.csv, a
hand copy of https://openalex.org/institutional-supporters made on 24 Nov 2026 (tier, name, country, type; the page
needs a browser). Countries were set from the name or, if unclear, an OpenAlex institutions search; 13 stayed
unresolved. Types were set by hand from the name. Output: results/supporters.json (counts only, no names)."""
import collections, csv, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
rows = list(csv.DictReader(open(os.path.join(HERE, '..', 'data', '_private', 'supporters_countries.csv'))))
by_country = collections.Counter(r['country_code'] or 'unresolved' for r in rows)
out = {'pulled': '2026-11-24', 'url': 'https://openalex.org/institutional-supporters', 'total': len(rows),
       'by_tier': dict(collections.Counter(r['tier'] for r in rows)),
       'by_type': dict(collections.Counter(r['type'] for r in rows)),
       'unresolved_country': by_country.pop('unresolved', 0),
       'by_country': dict(by_country.most_common())}
json.dump(out, open(os.path.join(HERE, '..', 'results', 'supporters.json'), 'w'), indent=1)
print(json.dumps(out, indent=1))
