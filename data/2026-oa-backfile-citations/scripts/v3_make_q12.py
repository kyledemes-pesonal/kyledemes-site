"""v3 (22 Nov 2026): writes scripts/v3_q12_prefix_panel.sql. Same 1,771 sources and cited set as Q08/Q10, with the unit
split by the cited record's DOI prefix (pfx = '10.NNNN', or 'none' when the record has no DOI), so JSTOR 10.2307 duplicate
records and records without the journal's own prefix can be dropped in Python. Outcomes per citing year: all served edges
(cites); deduplicated journal articles/reviews (cites_ja); edges whose only provenance is the repository/PDF lane
(cites_repo_only); dedup journal articles/reviews with an edge filed on the DOI record, provenance 'crossref' (cites_ja_cr;
since Nov 2026 that label also covers PDF and landing-page lists filed on DOI records). Same definitions as Q10."""
import re, os
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ids = re.search(r'bigint\) IN \(([0-9,]+)\)', open('scripts/q08_citation_panel.sql').read()).group(1)
print(len(ids.split(',')), 'sources')
sql = f"""-- v3 Q12 (22 Nov 2026): citation panel by DOI prefix of the cited record, same sources as Q08 (written by v3_make_q12.py).
WITH cited AS (
  SELECT id, cast(regexp_extract(primary_location.source.id, '(\\\\d+)$', 1) AS bigint) src, publication_year py,
    coalesce(nullif(regexp_extract(lower(coalesce(doi, '')), '(10\\\\.[0-9]+)/', 1), ''), 'none') pfx
  FROM openalex.works.openalex_works
  WHERE type IN ('article','review') AND publication_year BETWEEN 1880 AND 2023
    AND cast(regexp_extract(primary_location.source.id, '(\\\\d+)$', 1) AS bigint) IN ({ids})),
sizes AS (SELECT src, py, pfx, count(*) n_articles FROM cited GROUP BY 1,2,3),
citing AS (
  SELECT id, publication_year cy,
    (type IN ('article','review') AND primary_location.source.type = 'journal' AND NOT coalesce(is_paratext, false)
      AND NOT coalesce(is_xpac, false)) ja,
    xxhash64(coalesce(lower(doi), concat(regexp_replace(lower(coalesce(title, cast(id AS string))), '[^a-z0-9]', ''), '|', cast(publication_year AS string)))) ckey
  FROM openalex.works.openalex_works WHERE publication_year BETWEEN 1995 AND 2025),
cites AS (
  SELECT c.src, c.py, c.pfx, g.cy, count(*) cites,
    count(DISTINCT CASE WHEN g.ja THEN xxhash64(g.ckey, c.id) END) cites_ja,
    sum(CASE WHEN size(e.sources) > 0 AND forall(e.sources, s -> s.provenance = 'repo') THEN 1 ELSE 0 END) cites_repo_only,
    count(DISTINCT CASE WHEN g.ja AND exists(e.sources, s -> s.provenance = 'crossref') THEN xxhash64(g.ckey, c.id) END) cites_ja_cr
  FROM openalex.works.work_citations e JOIN cited c ON e.cited_work_id = c.id JOIN citing g ON e.citing_work_id = g.id
  WHERE e.served GROUP BY 1,2,3,4)
SELECT s.src, s.py, s.pfx, s.n_articles, c.cy, coalesce(c.cites,0) cites, coalesce(c.cites_ja,0) cites_ja, coalesce(c.cites_repo_only,0) cites_repo_only, coalesce(c.cites_ja_cr,0) cites_ja_cr
FROM sizes s LEFT JOIN cites c ON s.src = c.src AND s.py = c.py AND s.pfx = c.pfx
"""
open('scripts/v3_q12_prefix_panel.sql', 'w').write(sql)
