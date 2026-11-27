-- Q02: per journal (first ISSN) x open-licence family x content version x licence start month:
-- articles whose open licence starts >=180 days after publication. Filter first, dedup by DOI (latest ingest) after.
WITH it AS (SELECT explode(items) i, ingested_at FROM openalex.crossref.crossref_items),
l AS (
  SELECT lower(i.DOI) doi, ingested_at, i.ISSN[0] issn, i.publisher publisher, i.`container-title`[0] journal,
    get(get(i.issued.`date-parts`,0),0) py, coalesce(get(get(i.issued.`date-parts`,0),1),1) pm,
    lic.URL url, lic.`content-version` cv, lic.`delay-in-days` delay,
    get(get(lic.start.`date-parts`,0),0) sy, coalesce(get(get(lic.start.`date-parts`,0),1),1) sm
  FROM it LATERAL VIEW explode(i.license) t AS lic
  WHERE i.type='journal-article' AND lic.`delay-in-days` >= 180),
o AS (
  SELECT *, try_to_date(concat_ws('-', cast(py as string), lpad(cast(pm as string),2,'0'), '01')) pub,
    try_to_date(concat_ws('-', cast(sy as string), lpad(cast(sm as string),2,'0'), '01')) start_m,
    CASE
    WHEN lower(url) LIKE '%creativecommons.org%' THEN 'cc'
    WHEN lower(url) LIKE '%elsevier.com/open-access/userlicense%' THEN 'elsevier_oa'
    WHEN lower(url) RLIKE 'pnas.org/site/(aboutpnas/licenses|misc/userlicense)|aspb.org/publications/aspb-journals/open-articles|biologists.com/user-licence|ametsoc.org/pubsreuselicenses|authorchoice|chorus|oa_license|open-access|openaccess|aps-default-accepted|ams.org/publications/copyright|apa.org/pubs/journals/resources/open-access|aip.org/authors/rights' THEN 'other_open'
    ELSE NULL END fam
  FROM l),
d AS (SELECT doi, fam, cv, max_by(struct(issn, publisher, journal, pub, delay, start_m), ingested_at) s
      FROM o WHERE fam IS NOT NULL GROUP BY doi, fam, cv)
SELECT s.issn issn, first(s.publisher) publisher, first(s.journal) journal, fam, cv, s.start_m start_m,
  count(*) n, min(year(s.pub)) pub_min, max(year(s.pub)) pub_max, percentile_approx(s.delay,0.5) delay_med
FROM d WHERE s.issn IS NOT NULL
GROUP BY s.issn, fam, cv, s.start_m
