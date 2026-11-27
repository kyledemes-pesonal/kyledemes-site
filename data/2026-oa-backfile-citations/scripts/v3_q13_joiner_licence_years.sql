-- v3 Q13 (22 Nov 2026): Elsevier open-archive user licence by publication year for six joiner journals (first ISSN),
-- to check how far back the open archive reaches (licence start month too). Dedup by DOI, latest ingest.
WITH it AS (SELECT explode(items) i, ingested_at FROM openalex.crossref.crossref_items),
x AS (
  SELECT lower(i.DOI) doi, ingested_at, i.ISSN[0] issn, get(get(i.issued.`date-parts`,0),0) py,
    exists(i.license, l -> lower(l.URL) LIKE '%elsevier.com/open-access/userlicense%') oa_lic,
    array_min(transform(filter(i.license, l -> lower(l.URL) LIKE '%elsevier.com/open-access/userlicense%'),
      l -> concat_ws('-', cast(get(get(l.start.`date-parts`,0),0) AS string), lpad(cast(coalesce(get(get(l.start.`date-parts`,0),1),1) AS string),2,'0')))) lic_start
  FROM it WHERE i.type = 'journal-article' AND i.ISSN[0] IN ('0042-6822','0005-2736','0042-6989','0923-2508','1063-4584','0954-6111','0005-2728','1631-073X')),
d AS (SELECT doi, max_by(struct(issn, py, oa_lic, lic_start), ingested_at) s FROM x GROUP BY doi)
SELECT s.issn, s.py, count(*) n, sum(CASE WHEN s.oa_lic THEN 1 ELSE 0 END) n_oa_lic, min(s.lic_start) lic_start_min, max(s.lic_start) lic_start_max
FROM d WHERE s.py BETWEEN 1985 AND 2022 GROUP BY 1,2 ORDER BY 1,2
