# Opening old papers barely changed how often they were cited: data and scripts

The numbers and the first chart behind the post [Opening old papers barely changed how often they were cited](https://kyledemes.com/notes/2026/opening-old-papers-citations/) (27 November 2026). Citations come from [OpenAlex](https://openalex.org) (CC0), as of 22 November 2026. `MANIFEST.md` maps every number and chart in the post to its script and file.

## What the analysis does

1. **Openings.** 113 dated cases, 2005 to 2024, where a publisher removed the paywall from a journal's already-published papers while its new papers stayed paywalled (apart from the usual delay). Dates come from publisher announcements, Crossref licence start dates and archived copies of publisher pages. The list is `results/v3/final_events_v3.tsv`; openings set aside, with the reason for each, are in `results/final_exclusions.tsv`.
2. **Comparison journals.** For each opening, up to five journals in the same OpenAlex subfield that never opened their back files, matched on citations per paper and their trend before the opening (`data/control_candidates.tsv` holds the 12 candidates per opening; the final five are chosen by `match` in `v2_common.py`, called through `match3` in `v3_common.py`).
3. **Citations.** Citations per journal, publication year and citing year, for the opened papers and the same publication years in the comparison journals, with duplicate and misfiled records dropped the same way for both.
4. **Model.** A Poisson regression of yearly citations, stacked by opening, from 5 years before to 10 years after, leaving out the opening year and comparing papers of the same age. Three weightings (by prior citations, by papers opened, each opening equally). Uncertainty allows for openings that shared a date (14 groups), with a score wild-cluster bootstrap.
5. **Checks.** A fake opening three years early, openings with two date sources, citations from journal articles only, papers of different ages at opening, the two mathematics programs, and papers only 1 to 2 years old at opening (`v4_*.py`).

## Where the data came from, and the public route

The citation panels were pulled from the OpenAlex data warehouse on Databricks, which is not public. The SQL is included (`scripts/*.sql`) so you can see exactly what was counted, and `dbx.py` / `dbx_big.py` are the small read-only helpers that ran it (they need a signed-in Databricks command line tool and `DATABRICKS_WAREHOUSE_ID`).

To rebuild the panels without the warehouse, use the same tables in the free [OpenAlex snapshot](https://docs.openalex.org/download-all-data/openalex-snapshot) (works, their locations and `referenced_works`), or, for a handful of journals, the [OpenAlex API](https://docs.openalex.org) with `group_by=publication_year` and `cites:` filters. The API changes daily, so counts will differ a little from the 22 November snapshot.

The panel extracts themselves (`data/q08_panel.csv`, `data/v2_q10_panel.csv`, `data/v3_q12_panel.csv`, 1.3 to 1.8 million rows each) and the journal attribute file (`data/q03_sources.json`) are not included: they are large, and the SQL regenerates them. Everything in `results/` is a count, an estimate or a list of journals.

## Run order

Run from this folder (the one holding `scripts/`, `data/` and `results/`). Python 3.10+ with pandas, numpy, scipy and pyfixest 0.70.

```
# 1. Warehouse pulls (write data/; need warehouse access)
python scripts/dbx.py scripts/q03_sources.sql data/q03_sources.json              # journal attributes (subfield, size, citedness)
python scripts/dbx.py scripts/q02_open_licence_start_by_journal.sql data/q02.json  # Crossref open-licence starts, for screening controls
python scripts/dbx.py scripts/q07_joiner_doi_prefix.sql data/q07.json             # Elsevier archive joiners: own DOI prefix before opening
python scripts/dbx_big.py scripts/q08_citation_panel.sql data/q08_panel.csv        # first citation panel (21 Nov; still read at import)
python scripts/dbx_big.py scripts/v2_q10_citing_split_panel.sql data/v2_q10_panel.csv  # arXiv copies, citing-side outcomes
python -I scripts/v3_make_q12.py                                                   # writes scripts/v3_q12_prefix_panel.sql
python scripts/dbx_big.py scripts/v3_q12_prefix_panel.sql data/v3_q12_panel.csv    # THE panel behind every v3 number (22 Nov)
python scripts/dbx.py scripts/v3_q13_joiner_licence_years.sql data/v3_q13.json    # joiners' licence years (shipped)

# 2. Events and controls (shipped as results; the web-scan inputs to the first two steps are not)
python -I scripts/final_events.py        # results/final_events.tsv, results/final_exclusions.tsv
python -I scripts/control_candidates.py  # data/control_candidates.tsv (shipped)
python -I scripts/v3_events.py           # results/v3/final_events_v3.tsv: cohort fixes, openings that didn't hold

# 3. Estimates
python -I scripts/v3_estimands.py        # results/v3/estimands.json, stacks_v3.tsv: headline, without Cell Press, leave one program out
python -I scripts/v3_extras.py           # results/v3/extras.json, chart1_raw_balanced.json, event_study_v3.tsv, ...
python -I scripts/v3_more.py             # results/v3/more.json: openings 2015-2024 vs 2005-2014
python -I scripts/v3_bridge.py           # results/v3/bridge.json: v2 to v3, one fix at a time
python -I scripts/v3_joiner_dates.py     # results/v3/joiner_dates.json
python -I scripts/v3_make_q14.py; python scripts/dbx.py scripts/v3_q14_citing_pool_coverage.sql data/v3_q14_coverage.json  # reference-list coverage (shipped)
python -I scripts/v3_arxiv_share.py      # results/v3/arxiv_share.json
python -I scripts/v2_prior_citing.py     # results/v2/prior_citing.json: arXiv split ("gained no less")
python -I scripts/estimate_within.py     # results/estimates_within.json: Annual Reviews within-journal test (first panel)
python -I scripts/v4_counts.py; python -I scripts/v4_estimates.py; python -I scripts/v4_followup.py  # papers 1-2 years old at opening
```

`v2_common.py` and `v3_common.py` are shared modules (matching, panel, model, bootstrap); every v3 and v4 script imports them, and `v2_common.py` reads `data/q08_panel.csv` and `data/q03_sources.json` when imported. `estimate.py` is the first version of the model, kept because `estimate_within.py` loads it. `scripts/v3_api/` holds the live API check used to confirm which publication years an archive opened.

The analysis went through three rounds (v1, v2, v3), each fixing what checks of the last one found; v3 is the one in the post, and `results/v3/bridge.json` shows how the numbers moved from v2 to v3 one fix at a time.

## Edited for publication

The scripts are as run, except: `dbx.py` reads the warehouse ID from the environment instead of a hard-coded value; `v4_counts.py`, `v4_estimates.py` and `v4_followup.py` find their folder from their own location instead of a local path; `v3_api/oa.py` reads an optional `OPENALEX_API_KEY` from the environment and logs next to itself. In `v2_common.py`, `v4_estimates.py` and `v4_followup.py`, comments and one constant (`SIX_POINT_WEIGHTS`) were renamed so that no researcher's name appears; the code does the same thing. `v3_arxiv_share.py` was written for this folder to save a count made during the analysis (it reproduces it: 8,783 of 352,540 papers). Some docstrings still give the original run command (`.venv/bin/python -I scripts/...`): any Python with the packages above works.

## What's in `results/` and `data/`

| File | What it holds |
| --- | --- |
| `results/v3/final_events_v3.tsv` | Every dated opening: journal, OpenAlex source ID, program, year opened, publication years opened, date sources, status in v3 (`pure` = in the headline) and why |
| `results/final_events.tsv`, `results/final_exclusions.tsv` | The first event list and the openings set aside, with a reason each |
| `results/v3/stacks_v3.tsv` | Each opening with its five (or fewer) comparison journals and its program-date group |
| `results/v3/estimands.json` | Headline estimates: three weightings, bootstrap intervals and p-values, smallest detectable effects, without Cell Press, leaving out one program at a time |
| `results/v3/extras.json` | Counts, placebo, event study, chart 1, mathematics split, age at opening, two-date-source subset, citing-side outcomes, record-cleaning counts |
| `results/v3/chart1_raw_balanced.json` | The rows of chart 1 |
| `results/v3/event_study_v3.tsv` | Year-by-year estimates from 5 years before to 10 after |
| `results/v3/provenance_by_year_v3.tsv` | Where citations came from (journal articles, repository-only), by citing year |
| `results/v3/fix3_record_diagnostics.tsv` | Records dropped as duplicates or misfiled, per journal |
| `results/v3/bridge.json`, `more.json`, `joiner_dates.json`, `arxiv_share.json` | The v2 to v3 bridge; openings by period; a dating check; arXiv copies before opening |
| `results/v2/prior_citing.json` | v2 estimates split by whether a paper had an arXiv copy before the opening, and other citing-side checks |
| `results/estimates_within.json` | Opened against closed volumes inside the same journals (Annual Reviews 2023, Royal Society 2011) |
| `results/v4_recent/*` | Papers 1 to 2 years old at opening: counts per opening, estimates, placebos |
| `data/control_candidates.tsv`, `data/elsevier_joiners.tsv` | Comparison-journal candidates per opening; Elsevier open-archive joiners with join window, embargo and first year covered |
| `data/v3_q13.json`, `data/v3_q14_coverage.json` | Joiners' Crossref licence share by year; share of citing papers with a reference list, opened vs comparison journals, by year |

## Check it in a browser

The Journal of Mathematical Analysis and Applications, one of the Elsevier mathematics journals opened in 2012: its 1960-2008 papers are almost all free to read today (about 18,100 of 18,300 "bronze"):
<https://api.openalex.org/works?filter=primary_location.source.id:S151579836,publication_year:1960-2008,type:article|review&group_by=open_access.oa_status>

One of its comparison journals, the Ukrainian Mathematical Journal, over the same years: about 9 in 10 still closed:
<https://api.openalex.org/works?filter=primary_location.source.id:S145196850,publication_year:1960-2008,type:article|review&group_by=open_access.is_oa>

Cell's 1995-2003 papers, opened by Cell Press in 2005: about 3,770 of 3,850 free today:
<https://api.openalex.org/works?filter=primary_location.source.id:S110447773,publication_year:1995-2003,type:article|review&group_by=open_access.is_oa>

Open status today confirms the archive is open; it doesn't date the opening, which comes from the publishers' own records.

## Known limits

- Openings are dated to the year, and the opening year itself is left out. Most Elsevier archive joiners are dated between two archived captures of the archive's list, so some could be off by a year.
- Comparison journals were screened for any sign of opening, but some may have free copies elsewhere (repositories, preprints).
- OpenAlex lacks reference lists for some citing papers (roughly one in eight in a typical year, 13% weighted by citations), similarly for both groups (`data/v3_q14_coverage.json`).
- About half the openings come from two mathematics programs, and about 50 Elsevier mathematics journals share one opening date, so the uncertainty is wide.
