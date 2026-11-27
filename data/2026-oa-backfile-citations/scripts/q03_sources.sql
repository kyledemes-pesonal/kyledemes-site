-- Q03: journal sources with matching covariates (field/subfield = largest topic_share entry), for treated mapping and control pool
WITH s AS (
SELECT id, issn_l, issn, display_name, host_organization_name, country_code, works_count, cited_by_count,
  summary_stats.`2yr_mean_citedness` c2, is_in_doaj, is_in_doaj_since_year, oa_flip_year, is_oa,
  first_publication_year, last_publication_year, is_core,
  array_max(transform(topic_share, x -> struct(x.value v, x.field.display_name field, x.subfield.display_name subfield))) top
FROM openalex.sources.sources_api
WHERE type = 'journal' AND works_count >= 100)
SELECT * EXCEPT (top), top.field field, top.subfield subfield FROM s
