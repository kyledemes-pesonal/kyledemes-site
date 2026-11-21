# Where Canada's open research lives: data and scripts

The numbers behind the post [Where Canada's open research lives](https://kyledemes.com/notes/2026/where-canadas-open-research-lives/) and its Canadian Open Access Monitor (`monitor.html`). All data comes from the [OpenAlex API](https://docs.openalex.org) (CC0).

## Run order

```
export OPENALEX_API_KEY=...   # optional but recommended; about 150 requests
python3 scripts/build_monitor.py
python3 scripts/make_figure.py   # the post's figure (needs matplotlib)
python3 scripts/build_trends.py  # the two trend charts (trends.html): every Canadian university and province, every country (about 90 requests)
python3 scripts/universities.py  # optional: the university policy tests, not used in the post (about 60 requests)
```

Standard library only (`make_figure.py` also needs matplotlib). The scripts rewrite `results/` and rebuild `monitor.html` and `trends.html` from the templates in `scripts/`. All four take about two minutes. The "data as of" date on both pages is the day you run them. `MANIFEST.md` maps every number and chart in the post to its script and file.

## What's in `results/`

| File | What it holds |
| --- | --- |
| `routes_by_year.csv` | Papers by year and OA route (gold, diamond, hybrid, green, bronze, closed), plus copies in a Canadian repository and in PubMed Central, for all Canadian research, the tri-agencies combined and each agency |
| `grant_numbers_by_year.csv` | Papers per agency and year, and how many carry that agency's grant number |
| `closed_by_publisher.csv` | Tri-agency papers from the latest year with no free copy, by publisher, with each publisher's zero-embargo policy and a link to it |
| `open_by_field.csv` | Tri-agency papers from the latest year by field: total, free to read, closed |
| `funders.csv` | Share of each funder's latest-year papers that are free to read |
| `kpi_comparison.csv` | The agencies' 2025 KPI baselines beside the OpenAlex figures |
| `canadian_repositories.csv` | The 100 Canadian repositories counted as "Canadian repository copy" |
| `monitor_data.json` | Everything above in the form the dashboard reads |
| `oa_by_university.csv` | Papers and free-to-read papers per year, 2010-2026, for each Canadian university with at least 1,000 papers since 2010 (top-level institutions only; campuses and faculties roll up), with its province and whether it's in the U15 |
| `oa_by_province.csv` | The same for all research with an author in each province or territory, and for Canada |
| `oa_by_country.csv` | The same for each country with at least 5,000 papers since 2010, and for the world (every paper with an author affiliation) |
| `trends_data.json` | Everything above in the form `trends.html` reads |
| `university_oa_by_year.csv` | Input to the policy tests (not used in the post): journal articles (2010-2025) for Canada and 30 universities (the U15 and 15 more) by year and OA route, plus copies in a Canadian repository |
| `policy_timeline.csv` | Not used in the post. 252 university and national events (policies, APC funds, repositories, CRKN agreements, federal policy), each with its source and a `verified` flag: `yes` means a page we opened states the event (and its date, where one is given); `partial` means the page confirms the event but the date is inferred (a first Wayback capture, earliest deposit, registry date, fiscal-year report or "since" wording) or only the year is stated. Rows we couldn't confirm at a source were removed on 20 Nov 2026. Rows with `tested` set are the ones tested |
| `policy_event_tests.csv` | Not used in the post. Each tested event: the change in the three years after against the three years before, net of Canada's change, and its rank against the other 29 universities in the same years (1 = largest gain) |

## Check the headline numbers in a browser

Tri-agency papers (articles and reviews, 2025):
<https://api.openalex.org/works?filter=type:article|review,publication_year:2025,funders.id:F4320334506|F4320321563|F3340254956|F8543264415|F4320324195|F4320334593|F4320321487|F4320334617|F7697234222|F4320320994|F4320321481|F4320326644>

Of those, free to read (add `is_oa:true`):
<https://api.openalex.org/works?filter=type:article|review,publication_year:2025,funders.id:F4320334506|F4320321563|F3340254956|F8543264415|F4320324195|F4320334593|F4320321487|F4320334617|F7697234222|F4320320994|F4320321481|F4320326644,is_oa:true>

By OA route:
<https://api.openalex.org/works?filter=type:article|review,publication_year:2025,funders.id:F4320334506|F4320321563|F3340254956|F8543264415|F4320324195|F4320334593|F4320321487|F4320334617|F7697234222|F4320320994|F4320321481|F4320326644&group_by=oa_status>

All Canadian research, by OA route:
<https://api.openalex.org/works?filter=type:article|review,publication_year:2025,institutions.country_code:CA&group_by=oa_status>

CIHR papers carrying a CIHR grant number:
<https://api.openalex.org/works?filter=type:article|review,publication_year:2025,funders.id:F4320334506|F4320321563|F3340254956|F8543264415|F4320324195,awards.funder_id:F4320334506|F4320321563|F3340254956|F8543264415|F4320324195>

## Definitions and caveats

- **Canadian:** at least one author with a Canadian affiliation, counted once.
- **Tri-agency:** funding metadata names CIHR, NSERC, SSHRC (or their programs), Canada Research Chairs, CERC or CFREF.
- **Free to read** is measured on the day of the run, not at publication.
- **Canadian repository copy** is a record in one of the repositories in `canadian_repositories.csv`. It depends on how fully OpenAlex harvests each repository, so treat it as what OpenAlex can see.
- **APC value** is each journal's list price for gold and hybrid papers, counted whole. It isn't what anyone paid.
- **Trend charts:** 2026 is a partial year (papers published so far). Universities are OpenAlex institutions of type education in Canada whose names mark them as universities, counted with everything under them in the OpenAlex hierarchy; the Université du Québec network is shown as its member universities. Provinces are matched on the location of each author's institution.
- **University tests** (set aside: none showed a clear signal) use the share open only through a repository (green) for institution-wide policies and the gold share for APC funds, with the overall open share alongside. A university counts if any author lists it (or a unit inside it). Events need two years on each side inside 2010-2025, so Ottawa's 2009 and Concordia's 2010 policies aren't tested. With ten policies tested, about one would rank in the top three of 30 by chance.
- **Known harvesting artefacts in the university data:** repository copies at SFU, Victoria, Carleton and York all jump in 2017 and fall back in 2018 (SFU's policy is also from 2017, so read that year with care); Windsor's copies swing by 13 to 20 points a year since 2020; INRS, UQAM, Concordia (2011-2013) and Laurier swing by 5 to 13 points; Western falls from 21% in 2019 to 4% in 2025, much faster than the country. Recent years are low everywhere because deposits lag publication.
- **Publisher policies** were read from the publishers' public pages on 18 Nov 2026.

## Reproduction check (20 Nov 2026)

All four scripts were re-run in a clean copy of this folder on 20 Nov 2026. Every file in `results/`, `monitor.html` and `trends.html` came out byte-identical to the published copies. `figure.png` was redrawn from the same results: the earlier copy had been drawn from the 19 Nov pull, and its labels (84%, 8%) didn't change. Removing the unconfirmed timeline rows changed no policy test. OpenAlex updates daily, so a later run will differ a little.

Corrections: kyle@demes.ca.
