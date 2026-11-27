"""Writes scripts/v2_q11_citing_pool_coverage.sql: reference coverage of the citing pools of treated vs control journals
(v2 pure set, v1 matching). Pool weights = citation edges from works published 1995-2025 to articles/reviews of the pool's
sources (publication years <= 2023); coverage per citing source x year = share of its articles/reviews with a non-empty
reference list. Output: pool x citing year weighted coverage, plus the unweighted coverage of all journal articles/reviews."""
import sys; sys.path.insert(0, 'scripts')
from v2_common import *
st, units = match()
pure = st[(st.group == 'pure') & (st.platform_move == 0)]
T = sorted(set(pure.treated)); C = sorted(set(int(c) for cs in pure.controls for c in cs.split()) - set(T))
q = f"""-- v2 Q11: citing-pool reference coverage, treated ({len(T)} pure-opening journals) vs their controls ({len(C)} journals).
WITH pool AS (
  SELECT id, CASE WHEN src IN ({','.join(map(str, T))}) THEN 'treated' ELSE 'control' END pool FROM (
    SELECT id, cast(regexp_extract(primary_location.source.id, '(\\\\d+)$', 1) AS bigint) src
    FROM openalex.works.openalex_works WHERE type IN ('article','review') AND publication_year <= 2023) x
  WHERE src IN ({','.join(map(str, T + C))})),
w AS (
  SELECT p.pool, g.primary_location.source.id csrc, g.publication_year cy, count(*) n_edges
  FROM openalex.works.work_citations e JOIN pool p ON e.cited_work_id = p.id JOIN openalex.works.openalex_works g ON e.citing_work_id = g.id
  WHERE e.served AND g.publication_year BETWEEN 1995 AND 2025 AND g.primary_location.source.id IS NOT NULL GROUP BY 1,2,3),
cov AS (
  SELECT primary_location.source.id csrc, publication_year cy, count(*) n, sum(CASE WHEN referenced_works_count > 0 THEN 1 ELSE 0 END) n_ref,
    sum(CASE WHEN coalesce(indexed_in_crossref, false) THEN 1 ELSE 0 END) n_crossref
  FROM openalex.works.openalex_works WHERE type IN ('article','review') AND publication_year BETWEEN 1995 AND 2025
    AND primary_location.source.id IN (SELECT DISTINCT csrc FROM w) GROUP BY 1,2)
SELECT w.pool, w.cy, sum(w.n_edges) edges, count(*) n_citing_sources,
  sum(w.n_edges * c.n_ref / c.n) / sum(CASE WHEN c.n > 0 THEN w.n_edges END) cov_ref_weighted,
  sum(w.n_edges * c.n_crossref / c.n) / sum(CASE WHEN c.n > 0 THEN w.n_edges END) share_crossref_indexed_weighted
FROM w JOIN cov c ON w.csrc = c.csrc AND w.cy = c.cy GROUP BY 1,2 ORDER BY 1,2
"""
open('scripts/v2_q11_citing_pool_coverage.sql', 'w').write(q)
print(len(T), len(C))
