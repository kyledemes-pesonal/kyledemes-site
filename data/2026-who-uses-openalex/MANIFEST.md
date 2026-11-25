# Manifest: which script makes which number

Every chart and number in the post, the script that makes it, and where it lands in `results/`. Run scripts from `scripts/` in the order the README gives. "Corpus" = the 4,672 research papers (article, review, preprint, conference paper, book or chapter, dissertation, report) published 2022 to 24 November 2026 that the model labelled as using OpenAlex, with preprint and published versions of the same title counted once.

## Post section to file

| Post section | Number or chart | Script | File and field |
| --- | --- | --- | --- |
| Short version | 4,672 research papers | `analyse.py` | `summary.json` `corpus_size.papers` |
| | Probably 7,500 to 9,000 | `robustness.py` | `robustness.json` `estimate.estimate_with_user_share` (7,619) and `estimate_with_all_paper_share` (8,894) |
| | Half of this year's papers are reviews | `robustness.py` | `robustness.json` `reviews.2026` (1,581 of 3,192) |
| | About 1 in 4 cite OpenAlex | `analyse.py` | `summary.json` `cites_openalex_paper` (938 of the 3,680 with a reference list in OpenAlex) |
| | Dutch, Swiss, German, Canadian researchers most for their size | `analyse.py` | `summary.json` `countries[]` `share_of_corpus_with_country` / `share_of_all_papers_with_country` |
| | Two different sets of funders | `awards_flow.py` | `awards_by_group.json` (see chart 5) |
| How do you find papers that used OpenAlex? | 9,768 works | `pull_candidates.py`, `analyse.py` | `summary.json` `funnel` (sum of `works`) |
| | Chart 1: 9 in 10 (title or abstract), 6 in 10 (body text) | `analyse.py`, `make_figures.py` | `summary.json` `funnel`: group `title_abstract` and `body_read`; used = roles `data_source` + `subject` + `tool`; only mentioned = `passing` + `false_positive`; can't tell = `unclear` (a `false_positive` where the model couldn't see the word counts as can't tell). `figures/1-mentions.jsx` |
| | Chart 1 caption: 8,557 shown, 1,211 not shown | `analyse.py` | `summary.json` `funnel` group `body_unread` (1,211) |
| How fast is it growing? | Chart 2; 148 (2023), 386, 917, 3,192 (2026) | `analyse.py`, `make_figures.py` | `summary.json` `years`; reviews per year from `use == literature_search` in the corpus. `figures/used_by_year.jsx` |
| | Not OpenAlex holding more papers | `denominators.py` | `denominators.json` `year_all` (9.4 to 11.9 million a year) |
| | Without prolific authors, 2026 still more than three times 2025 | `robustness.py` | `robustness.json` `prolific.ratio_without_prolific` (3.37; 2,961 vs 878) |
| | 1,581 reviews this year, 267 last year | `robustness.py` | `robustness.json` `reviews` |
| Who uses it, and for what? | 134 countries | `analyse.py` | `summary.json` `countries_meta.distinct_countries` |
| | US 572, China 339, Brazil 299 | `analyse.py` | `summary.json` `countries[].papers` |
| | Chart 3 and "about twice", "well under" | `analyse.py`, `make_figures.py` | `summary.json` `countries[]` (top 15): `share_of_corpus_with_country` against `share_of_all_papers_with_country` (denominator `denominators.json` `with_country_all`, 33,517,069). `figures/countries-use-vs-output.jsx` |
| | Library and information science 31% | `analyse.py` | primary-topic subfield in the corpus (1,428 of 4,672) |
| | Chart 4 | `analyse.py`, `make_figures.py` | `summary.json` `fields[]` `share_of_corpus` / `share_of_all_papers`. `figures/fields-use-vs-output.jsx` |
| | Reviews 42%, bibliometrics 29% | `analyse.py` | `summary.json` `uses` (`literature_search` 1,973, `bibliometric_analysis` 1,336, of 4,672) |
| Who pays? | About half grants, half members and customers | [US tax filing](https://projects.propublica.org/nonprofits/organizations/461599252), year to June 2025 | contributions and grants $2,388,800 of $4,275,757 (56%); typed into chart 5's rows |
| | Grant-makers: Arcadia, Wellcome, Navigation Fund, Schmidt Sciences | grant announcements | [Arcadia 2021](https://blog.openalex.org/arcadia-2021-grant/), [Arcadia 2024](https://blog.openalex.org/ourresearch-receives-7-5m-grant-from-arcadia-to-establish-openalex-a-milestone-development-for-open-science/), [Navigation Fund](https://blog.openalex.org/ourresearch-receives-688k-grant-from-navigation-fund-to-enhance-the-openalex-user-interface/), [Wellcome](https://grantnav.threesixtygiving.org/grant/360G-Wellcome-323416_Z_24_Z), [Schmidt Sciences](https://blog.openalex.org/linking-the-worlds-research-to-the-code-it-runs-on/) |
| | 139 listed members, mostly universities, 9 research funders | `supporters_summary.py` | `supporters.json` `total`, `by_type` |
| | 615 papers list 1,427 grants; 95% from funders that don't pay for OpenAlex | `awards_flow.py` | `awards_by_group.json` `papers_with_awards`, `distinct_awards`, group `both` (72) |
| | Chart 5 | `awards_flow.py`, `make_figures.py` | right side `awards_by_group.json` `groups[].grants`; left side the tax-filing split. `figures/who_pays_flow.jsx` |
| What this can't tell us | Full text for under half of recent papers | `denominators.py`, `robustness.py` | `robustness.json` `fulltext_share` (23.8 of 53.4 million, 45%) |
| | 1,136 papers without a readable copy | `robustness.py` | `robustness.json` `estimate.body_papers_unread` |
| How I did it | 9,578 and 1,477 | `pull_candidates.py` | `meta.count` of the saved pages (also the browser links in the README) |
| | Opus agreed on 194 of 200 | `check_agreement.py` | `agreement.json` `total.agree_used_or_not` |

## Charts

`figures/*.png` are renders of the Claude Docs chart modules in `figures/*.jsx`, which `make_figures.py` (with `charts.py`) writes from `results/`. Each module carries its numbers as rows, so a module is also a readable copy of its chart's data.
