# What if Canada had borrowed another country's open access policy? Data and scripts

The numbers and both charts behind the post [What if Canada had borrowed another country's open access policy?](https://kyledemes.com/notes/2026/canada-open-access-policy-designs/). All data comes from the [OpenAlex API](https://docs.openalex.org) (CC0), pulled on 22 and 23 November 2026, plus Crossref's public API for the funder check. `MANIFEST.md` maps every number and chart in the post to its script and file.

This folder reads two files from the earlier post's folder next to it ([`../2026-where-canadas-open-research-lives/results/`](../2026-where-canadas-open-research-lives/results/)): `oa_by_country.csv` (the country table) and `canadian_repositories.csv` (the 99 Canadian repositories behind "an open copy in Canada").

## Run order

```
export OPENALEX_API_KEY=...          # optional but recommended
python3 scripts/s1_canada_sets.py          # Canadian and tri-agency papers by year and OA route (~45 requests)
python3 scripts/s1_phasein.py              # award years read from grant numbers (~45 requests)
python3 scripts/s1_canadian_platforms.py   # funded papers free at a Canadian publisher (~20 requests)
python3 scripts/s1b_open_copies.py         # open copies in Canadian repositories, 2016-2025 (pages through tens of thousands of works; several minutes)
python3 scripts/s2_analogue_data.py        # OA routes by year for 16 countries and 23 funders (~80 requests)
python3 scripts/s2_funded_vs_national.py   # funded papers against their country's papers, 2015 and 2025 (~110 requests)
python3 scripts/s2_analogue_tests.py       # before/after against peers (no API calls)
python3 scripts/s4_scenarios.py            # phase-in, ceiling arithmetic, rank thresholds (no API calls)
python3 scripts/s5_projection_paths.py     # the projections behind both charts (no API calls)

python3 checks/crossref_funder_sample.py 2024 2025   # funder detection check against Crossref (~80 requests)
python3 checks/applicant_share.py                    # reach of a UK-style rule (~600 requests)
```

Python 3.9 or later, standard library only. Each script rewrites its file in `results/` (or `checks/`). OpenAlex updates daily, so a later run will differ a little, and funder links to older papers were still being added while I worked (see below).

## What's in `results/`

| File | What it holds |
| --- | --- |
| `s1_canada_sets.json` | 2010-2025 by year: papers by OA route, copies in a Canadian repository, any repository copy, full-text splits, for all Canadian papers, tri-agency-funded Canadian papers, each agency, and tri-agency papers with any author |
| `s1_phasein_lags.json` | For 1,000 random funded Canadian papers per year (2017-2025) with an NSERC, SSHRC or Canada Research Chairs grant number: how many years separate the paper from the newest award year readable in its grant numbers |
| `s1_canadian_platforms.json` | Tri-agency-funded papers at Canadian publishers by OA status, 2023-2025 (the "trusted Canadian platform" route) |
| `s1b_open_copies.json` | Tri-agency-funded Canadian papers with a record in one of the 99 Canadian repositories, and with an open copy there, 2016-2025 (chart 2's measured line) |
| `s2_analogue_sets.json` | 2004-2025 by year: papers by OA route and any repository copy for 16 high-income countries and 23 funders |
| `s2_funded_vs_national.json` | For 14 funders, 2015 and 2025: the country's papers, the funded papers with an author in that country, and how many of each are free to read |
| `analogue_tests.csv`, `.json` | Each policy's change in open share from the year before it started to 3, 4 and 5 years after, against the median change of peers (15 other countries, or other funders), by route, plus the share of the closed gap closed |
| `scenarios.json` | Phase-in (share of funded papers from grants awarded from 2027, by publication year), the ceiling arithmetic, Canada's 2025 rank and the points needed to reach each rank. Its `scenarios` block is an earlier version of the projections, kept because the script writes it; the post uses `projections.json` |
| `projections.json`, `.csv` | Both charts: measured history and, for each design, low, high and middle estimates by year to 2030, with every assumption written into `params` |

## What's in `checks/`

| File | What it holds |
| --- | --- |
| `crossref_funder_sample.json` | Random samples of about 1,600 Canadian papers with DOIs (2024 and 2025): how open tri-agency-funded papers are when funding is detected from Crossref alone, against OpenAlex's tags. The 2024 sample was looked up one DOI at a time on 22 November and the 2025 sample in batches of 50 on 23 November; the script batches both |
| `applicant_share.json` | Random sample of 600 Canadian 2024 papers: share with a Canadian author who has at least 1, 3 or 5 tri-agency-funded papers since 2019 (aggregates only; the script uses author IDs inside its queries and saves none) |
| `university_own_repository.csv` | For 71 Canadian universities with at least 200 articles in 2024-25: the share with a record, and with an open copy, in the university's own repository. Computed from the OpenAlex data snapshot rather than the API: a location counts when its source is a repository whose host organization is the university or an institution in its lineage. Two registry gaps found on 22 November were corrected by hand (UQAM's repository was linked to another institution; Carleton's had no institution link) |

## Check the headline numbers in a browser

Canadian papers, 2025, by OA route (122,884 on 23 November):
<https://api.openalex.org/works?filter=type:article|review,publication_year:2025,institutions.country_code:CA&group_by=oa_status>

Tri-agency-funded Canadian papers, 2025, by OA route (32,615):
<https://api.openalex.org/works?filter=type:article|review,publication_year:2025,institutions.country_code:CA,funders.id:F4320334506|F4320321563|F3340254956|F8543264415|F4320324195|F4320334593|F4320321487|F4320334617|F7697234222|F4320320994|F4320321481|F4320326644&group_by=oa_status>

The same papers with any author, as the monitor counted them:
<https://api.openalex.org/works?filter=type:article|review,publication_year:2025,funders.id:F4320334506|F4320321563|F3340254956|F8543264415|F4320324195|F4320334593|F4320321487|F4320334617|F7697234222|F4320320994|F4320321481|F4320326644&group_by=oa_status>

NIH-funded papers with a repository copy, 2007 and 2009 (change the year):
<https://api.openalex.org/works?filter=type:article|review,publication_year:2007,funders.id:F4320332161,open_access.any_repository_has_fulltext:true>

Free-to-read papers by country, 2025, for the 16 high-income countries (remove `,is_oa:true` for the totals):
<https://api.openalex.org/works?filter=type:article|review,publication_year:2025,institutions.country_code:CA|US|GB|NL|DE|FR|SE|NO|FI|CH|AT|AU|JP|ES|IT|KR,is_oa:true&group_by=institutions.country_code>

## Definitions and caveats

- **Canadian:** at least one author with a Canadian affiliation, counted once. **Tri-agency-funded:** a Canadian paper whose OpenAlex funders include one of the 12 agency records listed in `scripts/oa.py`.
- **Free to read** is OpenAlex's `is_oa` on the day of the run (any version, any licence, including preprints OpenAlex has attached to the paper), not on publication day.
- **An open copy in Canada** is a location with `is_oa` at one of the 99 repositories in the monitor's list. It depends on how fully OpenAlex harvests each repository, so treat it as what OpenAlex can see. Several Canadian repository feeds were being fixed while I wrote this.
- **Funder links to older papers moved while I worked.** Between 22 and 23 November OpenAlex linked 9% more 2014 papers to the agencies, most of them closed. Everything here was re-run on 23 November; treat funder comparisons before about 2017 as rough. The country comparisons don't use funder data.
- **Projections are sketches, not forecasts.** Everything except the design is held at its 2025 level, and each range pairs my most cautious assumptions with my most generous ones. The `params` block of each design in `projections.json` and the table in the post say where each assumption comes from.

## Reproduction check (23 Nov 2026)

`s2_analogue_tests.py`, `s4_scenarios.py` and `s5_projection_paths.py` were re-run from a clean copy of this folder with Python 3.9; `analogue_tests.csv`, `analogue_tests.json`, `scenarios.json`, `projections.json` and `projections.csv` came out byte-identical. `s2_funded_vs_national.py` was re-run against the live API the same day and returned the same counts. The other API scripts were not re-run for this check.

Corrections: kyle@demes.ca.
