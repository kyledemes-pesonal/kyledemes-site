# Has research security policy changed who Canada works with? Data and code

Everything behind the field note of the same name. All counts come from [OpenAlex](https://openalex.org), pulled 16 to 20 November 2026; later pulls will differ a little as OpenAlex updates.

## Check the headline numbers in a browser

Each link returns counts grouped by country: the `CA` row is the total, the other row is the part with a co-author in that country. Change `2025` to `2020` to see the starting point.

- Canadian articles in 2025 with a Chinese co-author (about 10%): https://api.openalex.org/works?filter=type:article,institutions.country_code:CA,publication_year:2025&group_by=institutions.country_code
- The same for articles crediting NSERC, CIHR, SSHRC or CFI: https://api.openalex.org/works?filter=type:article,institutions.country_code:CA,publication_year:2025,funders.id:F4320334593|F4320334506|F4320334617|F4320319952|F4320320995&group_by=institutions.country_code
- The same, only articles with full text in OpenAlex (where grant credits are recorded most reliably): https://api.openalex.org/works?filter=type:article,institutions.country_code:CA,publication_year:2025,has_fulltext:true,funders.id:F4320334593|F4320334506|F4320334617|F4320319952|F4320320995&group_by=institutions.country_code
- Canada–China articles by year: https://api.openalex.org/works?filter=type:article,institutions.country_code:CA,institutions.country_code:CN&group_by=publication_year
- Canadian works whose full text mentions Huawei, 2016–2025 (1,694 when pulled on 19 November; the count grows as OpenAlex adds full text): https://api.openalex.org/works?filter=fulltext.search:huawei,institutions.country_code:CA,publication_year:2016-2025&group_by=publication_year

## What's here

`MANIFEST.md` maps every chart and number in the post to the script that makes it, the order to run them, and the output file and field.

- `results/` holds the aggregate outputs behind every number and chart:
  - `pairs.json`, `chart_c1_shares.json`: country-pair counts and the share of Canadian articles with a co-author in each country.
  - `pairs_wide.json`, `event_study_wide.json`, `event_study.json`: the 24-country comparison (and the earlier 8-country version).
  - `nro_list_saved.json`, `nro_map.csv`, `nro_controls.csv`, `nro_own_output.json`: the 103 Named Research Organizations matched to OpenAlex, the 247 unlisted Chinese institutions used for comparison, and each group's own output.
  - `nro_field_works.json`, `chart_nro_sensitive_works.json`: listed vs unlisted organizations by field, 24 countries.
  - `nro_verification_verdicts.csv`, `nro_verification_manual.csv`: the check on every Canadian paper linked to a listed organization (work ID, checks and verdict), and the 15 hand decisions.
  - `nro_funded_split_verified.json`, `chart_f2_nro_split.json`: listed organizations, funded vs other papers.
  - `funded_fulltext.json`, `chart_funded_fulltext_{f1,c4,c5,peers}.json`, `funder_coverage.json`: funded vs other papers, Canada, 19 partners and 8 peers, sensitive vs other fields, on full-text papers and on all papers.
  - `panel_rebase.json`, `panel_checks.json`, `panel_status.json`: the researcher panel, its robustness checks, and where cohort members went (counts only).
  - `where.json`, `lead_author.json`, `lead_corresp.json`, `provinces_v2.json`: universities, who leads, provinces.
  - `huawei_papers.json`, `huawei_national_v2_summary.json`, `nserc_huawei_summary.json`, `nserc_country_partners.json`: Huawei, aggregated.
- `scripts/` holds the Python that produced them (standard library only). Set `OPENALEX_API_KEY` in your environment (free from openalex.org; the full-text content API needs it), then run from `scripts/`. Scripts read from and write to `../results/`. `oa.py` is the shared API helper.
- `policy_timeline.md` and `huawei_timeline.md` list the policy and news timeline with sources.
- `checks/` holds the side checks quoted in the post (run from `checks/`; they write next to themselves):
  - `composition.py`: about a third of the drop in the funded share of Canada–China papers comes from the shift toward China-led papers (reads `../results/lead_author.json`).
  - `journal_share.py`: 98% of the articles counted are in journals.
  - `fulltext_coverage.py`: OpenAlex has full text for about half of Canadian articles. In a browser: [all Canadian articles 2016–2025 by full-text status](https://api.openalex.org/works?filter=type:article,institutions.country_code:CA,publication_year:2016-2025&group_by=has_fulltext), and [computer science and engineering only](https://api.openalex.org/works?filter=type:article,institutions.country_code:CA,publication_year:2016-2025,primary_topic.field.id:17|22&group_by=has_fulltext) (about a third).
  - `funder_recall/`: how often OpenAlex's funder field catches a tri-agency or CFI credit that the acknowledgement text makes (93–97% on papers with full text). The pipeline runs `sample.py`, `meta.py`, `fetch_tei.py`, `classify.py`, `analyze.py`, `model.py`; the per-paper decisions are included without the acknowledgement text.

## Not included, on purpose

Individual-level files aren't published: the author cohorts behind the researcher panel, the 1.1 million-article local download (re-create it with `scripts/pull_ca_works.py`), raw affiliation strings, acknowledgement text, and grant-level NSERC rows (applicant names and titles are in NSERC's own open data; download links in `MANIFEST.md`). The scripts re-create these files locally when you run them. The grant-matching test in the post isn't included, because it matches researchers to grants by name. The analysis reports institutions and countries, not people.

## Corrections disclosed

On 19 November 2026 I submitted 763 affiliation corrections to OpenAlex, mostly separating Shahid Beheshti University from Shahid Beheshti University of Medical Sciences. They change the data reported here, mostly for Iran.
