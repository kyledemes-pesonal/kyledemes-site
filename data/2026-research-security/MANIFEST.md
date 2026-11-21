# Manifest: which script makes which number

Every chart and number in the post, the script that makes it, and where it lands in `results/`. Run scripts from `scripts/` (`cd scripts; python X.py`) with `OPENALEX_API_KEY` set. Python 3.9+, standard library only.

## Run order

| Step | Command | Writes (in `results/`) | Time |
| --- | --- | --- | --- |
| 1 | `python pull_pairs.py` | `pairs.json` | ~5 min |
| 2 | `python pull_pairs_wide.py` | `pairs_wide.json` | ~2 min |
| 3 | `python did_wide.py`; `python did.py` | `event_study_wide.json`; `event_study.json` | seconds |
| 4 | `python parse_nro.py <saved list page>.html ../results/nro_list_saved.json` | `nro_list_saved.json` (shipped: the list as of 18 Apr 2024) | seconds |
| 5 | `python nro_map.py`; `python nro_controls.py` | `nro_map.csv`; `nro_controls.csv` | ~1 min |
| 6 | `python nro_field_works.py` | `nro_field_works.json`, `chart_nro_sensitive_works.json` | ~30 min |
| 7 | `python nro_own_output.py` | `nro_own_output.json` | ~3 min |
| 8 | `python pull_ca_works.py` | `ca_works/` (local only) | ~1 hour |
| 9 | `python verify_nro.py --pull`, then `python verify_nro.py --stats` | `nro_verification_verdicts.csv` (+ local `nro_verification.csv`, `nro_verification_stats.json`) | ~20 min |
| 10 | `VERIFIED=1 python author_panel.py` | `author_panel_verified.json` (local only) | ~1 min |
| 11 | `VERIFIED=1 python nro_funded_split.py` | `nro_funded_split_verified.json` | seconds |
| 12 | `python chart_data.py` | `chart_c1_shares.json`, `chart_f2_nro_split.json` | seconds |
| 13 | `VERIFIED=1 python panel_rebase.py`; `python panel_status.py` | `panel_rebase.json`; `panel_status.json` | ~2 min |
| 14 | `python funded_fulltext.py` | `funded_fulltext.json`, `chart_funded_fulltext_{f1,c4,c5,peers}.json` | ~5 min |
| 15 | `python funder_coverage.py` | `funder_coverage.json` | seconds |
| 16 | `python pull_where.py` | `where.json` | ~2 min |
| 17 | `VERIFIED=1 python lead_author.py`; `python lead_corresp.py` | `lead_author.json`; `lead_corresp.json` | ~10 min |
| 18 | `python pull_huawei.py`; `python huawei_national_v2.py --refresh` (calls `fetch_acks.py`) | `huawei_papers.json`; `huawei_national_v2_summary.json` | ~20 min |
| 19 | download NSERC files (below), then `python nserc_huawei.py`; `python nserc_country_partners.py` | `nserc_huawei_summary.json`; `nserc_country_partners.json` | seconds |
| 20 | `python provinces_v2.py` | `provinces_v2.json` | ~10 min |
| 21 | `python panel_checks.py` | `panel_checks.json` | ~2 min |

`oa.py` is the shared API helper. "Local only" files hold author IDs, raw affiliation strings or acknowledgement text and are not published.

## Post section to file

| Post section | Number or chart | Script | File and field |
| --- | --- | --- | --- |
| Pulled back at all? | Chart: share of Canadian articles with a co-author in each country; 9.8% (2020), 10.1% (2025) | `pull_pairs.py`, `chart_data.py` | `chart_c1_shares.json`; `pairs.json` `all.CA.<year>.CN / all.CA.<year>.CA` |
| | 2026 so far (Jan to Oct) | `pull_pairs.py` | `pairs.json` `all.CA.ytd2024..ytd2026` (printed by `chart_data.py`) |
| Everyone pulling back? | Chart and −23%, rank 2 of 24, US −38%, Canada series by year | `pull_pairs_wide.py`, `did_wide.py` | `event_study_wide.json` `CN.<country>.<year>` (log points; % = 100·(e^x − 1)); rank printed |
| | "22% to 25%" dropping any one country | `did_wide.py` | printed (leave-one-out line) |
| | earlier eight-country version, smaller papers and core journals | `did.py` | `event_study.json` `small` / `core` `.CN.CA` |
| Named organizations | Table (−32% / +13%, peers) and chart | `nro_map.py`, `nro_controls.py`, `nro_field_works.py` | `nro_field_works.json` `change.sens|nons.<country>.works_norm_pct`; `rank`; `ca_ci.bootstrap_95`; `ca_vs_peer_median_by_year`; chart `chart_nro_sensitive_works.json` |
| | 42% if counted as links | `nro_field_works.py` | `change.sens.CA.links_raw_pct` |
| | about 1% of China matches wrong; Iran 28% | `verify_nro.py --stats` | `nro_verification_stats.json` `by_country` (or count verdicts in `nro_verification_verdicts.csv`) |
| | Chart: funded 397 → 120 papers, index 49; other −15% | `author_panel.py`, `nro_own_output.py`, `nro_funded_split.py`, `chart_data.py` | `nro_funded_split_verified.json` `funded`, `other`, `*_counts`; chart `chart_f2_nro_split.json` |
| Policy or mood? | Chart: funded 9.0 → 6.1%, other 10.1 → 11.3% (all); 7.3 → 5.4% (full text); 9 countries | `funded_fulltext.py` | `funded_fulltext.json` `step1_canada_china`, `step3_peers_cn.{ft,all}.2019-20`; chart `chart_funded_fulltext_c4.json` (`lines`) + `chart_funded_fulltext_peers.json` |
| | Chart: 19 partners, median −14%, China before 2020 | `funded_fulltext.py` | `step2_partners19`; chart `chart_funded_fulltext_c4.json` (`bars`) |
| | 28% → 19% of papers with any funder | `funder_coverage.py` | `funder_coverage.json` `canada / any`, 2019 and 2025 |
| | full text tilt; "about 30%" | `funded_fulltext.py` | `step7_selection`, `step7c_recall_corrected_all_papers` |
| Sensitive stuff? | 21% vs 7%; ratios 0.57 → 0.29, 0.78 → 0.48; full text about a quarter each; chart | `funded_fulltext.py` | `step4_sensitive.{all,ft}.{sens,nonsens}`; chart `chart_funded_fulltext_c5.json` |
| Same researchers? | 2,587 / 10,994; table; −45%; unfunded 12% | `author_panel.py`, `panel_rebase.py` | `panel_rebase.json` |
| | interval 26% to 59%; ORCID-only 44%; pre-2021 windows 20 to 25% | `panel_checks.py` | `panel_checks.json` `cluster_bootstrap`, `orcid_only`, `windows` |
| | 57% vs 53% still in Canada; most others now in China | `panel_status.py` | `panel_status.json` `status`, `A.abroad_where` |
| Universities | Chart: U15 China shares; fields | `pull_where.py` | `where.json` `inst.<id>.{pre,post}.{CN,ALL}`, `fields` |
| Who leads? | First/last author tables | `lead_author.py` | `lead_author.json` `CN_all`, `CN_funded`, `NRO_all`, `US_all` by year |
| | Corresponding author; Canadian-led table | `lead_corresp.py` | `lead_corresp.json` `CN`, `NRO`, `US` (`corr_ca_any`, `has_corr`, `ca_lead_flc`, `n`) |
| Huawei | 1,694 candidates, 471 thank Huawei, 90 in funder field, by year, table | `huawei_national_v2.py`, `fetch_acks.py` | `huawei_national_v2_summary.json` |
| | Funder credits 53 (2023) → 12 (2025); ~250 co-authored a year | `pull_huawei.py` | `huawei_papers.json` `totals.funder`, `totals.coauthor` |
| | 132 NSERC grants, 33 new in FY2019, none from FY2021 | `nserc_huawei.py` | `nserc_huawei_summary.json` |
| | all NSERC partnerships fell (CRD to Alliance) | `nserc_country_partners.py` | `nserc_country_partners.json` `all` |
| Provinces | Table | `provinces_v2.py` | `provinces_v2.json` |

## Inputs that are not made by a script

- `nro_list_saved.json`: the Named Research Organizations list as published on 18 April 2024 (https://science.gc.ca/site/science/en/safeguarding-your-research/guidelines-and-tools-implement-research-security/sensitive-technology-research-and-affiliations-concern/named-research-organizations), parsed by `parse_nro.py`.
- `nro_map.csv`: the hand-checked match of all 103 listed organizations to OpenAlex; the matching is written out in `nro_map.py`, which re-fetches each record.
- `nro_controls.csv`: the 247 unlisted Chinese institutions used for comparison, as picked on 16 November 2026. `nro_controls.py` picks the largest institutions by current works count, so a re-run today can pick a slightly different set; the analysis scripts read this file.
- `nro_verification_manual.csv`: 15 hand decisions applied by `verify_nro.py` where its rules were ambiguous.
- NSERC open data (not shipped, about 570 MB), from NSERC's "Awards Data" on open.canada.ca: partner files `https://www.nserc-crsng.gc.ca/opendata/nserc_grt_fyr<YYYY>_partner.csv` (FY2012-2019) and `.../NSERC_FY<YYYY>_PARTNER.csv` (FY2020-2024), saved as `results/nserc_partners_raw/partner_<YYYY>.csv`; award files `.../nserc_grt_fyr<YYYY>_award.csv` (FY2013-2019) and the FY2020-2024 award files from the same dataset page, saved as `results/nserc_raw/award_<YYYY>.csv`.

## Not reproducible from this folder

The side checks that used to be here (funder-field recall, the composition share, journal share, full-text coverage) now have scripts in `checks/`, listed below.


- Grant matching ("Did they stop the work, or just stop crediting the grant?"): matches researchers to grant holders by name, so it isn't published.
- NUDT links 71 (2018) to 27 (2023): `https://api.openalex.org/works?filter=type:article,institutions.country_code:CA,institutions.country_code:CN,authorships.institutions.lineage:I170215575&group_by=publication_year` (on 20 November it returned 71 for 2018 and 25 for 2023).
- The 763 affiliation corrections submitted to OpenAlex on 19 November 2026.

## Reproduction check (20 November 2026)

The folder was copied to an empty `results/` and re-run against the live API. Headline numbers matched within rounding: Canada-China share 9.84% (2020) and 10.05% (2025) against 9.85% and 10.07%; the 24-country gap −22.7% against −23.1%, still second of 24; Canadian grants on 28.3% and 18.8% of funded Canada-China papers against 28.2% and 18.7%; U15 China shares within 0.2 points; corresponding-author shares within 1 point. `funded_fulltext.py` and the Canada and worldwide cells of `nro_field_works.py` (run with `--countries CA`) matched exactly. Scripts that read the local download were re-run on the 18 November download and reproduced their published files exactly. A live re-download of July to December 2025 matched that download to within 0.3% of works. `panel_status.py` reproduced the 57% and 53%; its 1,600-author sample of the comparison group is now drawn from a sorted list, so it is the same every run (the published sample was drawn before this fix). Counts for small partner countries move by more, as OpenAlex keeps updating.

## Side checks (`checks/`)

| Post claim | Script | Output |
|---|---|---|
| "That shift explains roughly a third of the drop" (shift toward China-led Canada–China papers) | `checks/composition.py` (needs `results/lead_author.json`) | `results/composition.json`: `composition_fraction_of_change` (0.32) |
| "all counts are articles (98% of them in journals)" | `checks/journal_share.py` | `checks/journal_share.json` |
| "full text for about half of Canadian articles, and about a third in computer science and engineering" | `checks/fulltext_coverage.py`, plus the two browser links in README | `checks/fulltext_coverage.json` |
| "where OpenAlex has a paper's full text, it catches more than nine in ten tri-agency credits" | `checks/funder_recall/` (sample, meta, fetch_tei, classify, analyze, model) | `checks/funder_recall/results.json`, `model.json`, `per_work.csv` (no acknowledgement text) |
