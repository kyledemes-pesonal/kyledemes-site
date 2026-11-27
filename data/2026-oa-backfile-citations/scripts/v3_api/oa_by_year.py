"""v3: OpenAlex API (live, 22 Nov 2026) share of articles/reviews closed today by publication year, for listed sources.
Usage: python oa_by_year.py S1,S2,... y0 y1 -> prints source, year, n, closed. Log: verify live_api/api_calls.log."""
import sys; from oa import get
for s in sys.argv[1].split(','):
    f = f"primary_location.source.id:S{s},publication_year:{sys.argv[2]}-{sys.argv[3]},type:article|review,open_access.is_oa:false"
    cl = {x['key']: x['count'] for x in get('works', filter=f, group_by='publication_year')['group_by']}
    f2 = f"primary_location.source.id:S{s},publication_year:{sys.argv[2]}-{sys.argv[3]},type:article|review"
    al = {x['key']: x['count'] for x in get('works', filter=f2, group_by='publication_year')['group_by']}
    print(s, ' '.join(f"{y}:{cl.get(y,0)}/{al[y]}" for y in sorted(al)))
