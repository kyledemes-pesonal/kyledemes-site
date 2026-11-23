# Manifest: which script makes which number

Every chart and number in the post, the script that makes it, and where it lands. Run the scripts from this folder (`python3 scripts/X.py`) with `OPENALEX_API_KEY` set; `README.md` has the run order. "Free to read" is `n − closed`; shares are `100 × column / n`. Rows marked *not in these scripts* were checked separately on the date shown.

## Charts

| Chart | Script | File and field |
| --- | --- | --- |
| 1. All Canadian papers free to read, measured 2016-2025 and projected to 2030 | `s5_projection_paths.py` | `results/projections.csv` rows `measure=national` (history from the monitor's `oa_by_country.csv`, `code=CA`); `projections.json` `scenarios[].national` = `[low, high, middle]` by year |
| 2. Tri-agency-funded papers with an open copy in Canada, measured 2016-2025 and projected to 2030 | `s1b_open_copies.py`, `s5_projection_paths.py` | history: `results/s1b_open_copies.json` `pct_open_copy` by year; projections: `projections.csv` rows `measure=home` |
| Image files | screenshots of the two charts in the draft | `figures/1-free-to-read-projections.png`, `figures/2-canadian-copy-projections.png` |

## The short version and "How far can the new policy move Canada's number?"

| Number | Script | File and field |
| --- | --- | --- |
| 32,615 of 122,884 Canadian papers (26.5%) acknowledge the agencies, 2025 | `s2_funded_vs_national.py` | `s2_funded_vs_national.json` `Tri-agency.2025` `funded / national` |
| Probably 28% to 30% once missed acknowledgements are allowed for | `checks/crossref_funder_sample.py` | `crossref_funder_sample.json` `imputed.share` (29.0% of the 2024 sample, 27.3% of the 2025 sample, each 1.5 points above that sample's tagged share); 30% is the upper end used throughout |
| 82% of funded papers free to read against 71% for the rest | `s2_funded_vs_national.py` | `Tri-agency.2025`: `funded_open / funded` = 26,736 / 32,615; rest = `(national_open − funded_open) / (national − funded)` = 71.5% |
| 74% (2024 sample) and 78% (2025 sample) with Crossref-only detection, against 72% for all Canadian papers | `checks/crossref_funder_sample.py` | `crossref_name.funded_open` 73.8 and 77.6; `national_open` 72.2 and 72.1 |
| The monitor's 84%, about 2,000 more papers linked since, about 60% of them open, 82.4% now; 82.0% Canadian-authored | *not in these scripts*; checked 23 Nov 2026 | the third and second browser links in `README.md` (any author: 83.8% in the monitor's data, 82.4% on 23 Nov; Canadian-authored 82.0%) |
| New grants behind 12% (2028), 37% (2030) and 85% (2033) of funded papers | `s1_phasein.py`, `s4_scenarios.py` | `scenarios.json` `phase_in_share_of_funded_papers_covered` 0.125, 0.372, 0.851 |
| About half in 2030 with the 2020-2022 lags | *not in these scripts*; same arithmetic as `s4_scenarios.py` with the 2020-2022 rows of `s1_phasein_lags.json` | 54% |
| Ceiling +0.8 to +2.3 points by 2030; +2 to +6 fully phased in | `s4_scenarios.py` | `scenarios.json` `ceiling[]`: `national_gain_2030_pts` 0.8 (OpenAlex tags, 90%) to 2.3 (Crossref view, 95%); `national_gain_full_phase_in_pts` 2.1 to 6.3 |
| Up to about +3.4 if the phase-in is faster | *not in these scripts*; the ceiling with the 2020-2022 lags | 1.1 to 3.4 |
| 74.3% free to read, 43rd of 55 countries with at least 20,000 papers; +1.7 for 40th, +8.2 for 30th | `s4_scenarios.py` | `scenarios.json` `baseline_2025.national_open_published_19nov`, `rank_of_55`, `points_needed_for_rank` `40`, `30` |
| NIH-funded 95% vs the US 70.5%; UKRI-funded 97% vs the UK 84% | `s2_funded_vs_national.py` | `NIH.2025`, `UKRI+councils.2025`: `funded_open / funded` and `national_open / national` |
| Every country 1 to 3 points above papers its main funder didn't fund | `s2_funded_vs_national.py` | `national_open / national` minus `(national_open − funded_open) / (national − funded)`, 2025, for each funder's country |
| 74% to 82% of funded papers already free to read; 90% to 95% targets | `checks/crossref_funder_sample.py`, `s2_funded_vs_national.py`, `s4_scenarios.py` | the two views in `scenarios.json` `ceiling[].funded_open_2025` (82.0, 74.0) and `target_funded_open` |

## What happened when other countries tried this?

Every row is in `results/analogue_tests.csv` (and `.json`), made by `s2_analogue_data.py` then `s2_analogue_tests.py`. Columns: `open_t+4` (change in free-to-read points from the year before to four years after), `open_t+4_peer_median`, `any_repo_t+4` and its `_excess`, `green_only_t+4_excess`, `closed_gap_cut_t+4` (share of the closed gap closed) and its `_peer_median`.

| Table row | `label` in `analogue_tests.csv` | Values used |
| --- | --- | --- |
| NIH law (2008): repository copies about half (2007), 76% (2008), 84% (2009); about 20 points more than other funders | `NIH 2008 law` (`kind=funder`) | `s2_analogue_sets.json` `funder:NIH` `anyrepo / routes.n`: 52.4, 75.7, 84.2; `any_repo_t+4_excess` 21.1 |
| Wellcome (2012): 81% to 95%, 73% of the closed gap against 30% | `Wellcome sanctions` | `open_level_pre` 81.4, `open_t+4` 13.5, `closed_gap_cut_t+4` 72.7, peer median 30.1 |
| RCUK and REF: UK +28.7 against +12.9; about 60% of the extra through repository copies | `RCUK policy + Finch (UK national)` | `open_t+4` 28.7, peer median 12.9; `green_only_t+4_excess` 9.9 of `open_t+4_excess` 15.8 |
| Once the REF rule took effect, the UK didn't pull further ahead | `REF deposit rule (UK national)` | `open_t+4_excess` −0.9 |
| Netherlands: overall share grew 4 points less than peers' (2020-2025), repository-only copies 5 more | `Institutional opt-out Taverne roll-out 2021-24 (NL national)` | `open_t+4_excess` −4.4; `green_only_t+4_excess` 4.9 |
| Netherlands 9% (2016) to 20% (2022) | *not in these scripts* | Universities of the Netherlands, letter on the 2022 open access monitor (linked in the post) |
| Finland, Sweden, Norway: +23 to +29 against 14.7 | `FinELib TAs`, `Bibsam TAs`, `National goal + deposit norm, Unit deals` | `open_t+4` 28.6, 25.5, 23.1; peer median 14.7 |
| NHMRC (2012): +10, about 3 less than other funders | `NHMRC 12-month deposit, unchecked` | `open_t+4` 10.0, `_excess` −2.6 |
| ARC (2013): +15.6, about 3 more | `ARC 12-month deposit` | `open_t+4` 15.6, `_excess` 3.4 |
| CIHR (2008): +7.8 against 13.3 | `CIHR 2008 policy` | `open_t+4` 7.8, peer median 13.3 |
| Canada (2015): +9.5 against 15.6; NSERC and SSHRC about 3 less than other funders | `Tri-agency harmonized policy (CA national)`, `Tri-agency 2015 (NSERC)`, `(SSHRC)` | `open_t+4` 9.5, peer median 15.6; `open_t+4_excess` −3.0 and −2.9 |
| Canada already slipping about 3 points behind peers in each five-year stretch before 2015 | *not in these scripts*; `s2_analogue_tests.py`'s `test()` run for `country:CA` with event years 2010 to 2014 | excess −3.8, −3.3, −3.6, −1.9, −2.6 (mean −3.0) |
| Hybrid 13% (2022) to 36% (2025) of tri-agency-funded papers | `s1_canada_sets.py` | `s1_canada_sets.json` `tri_ca.routes` `hybrid / n`: 13.4, 36.1 |
| Canada 74.3% and France 74.4% in 2025; 14 points behind in 2020 | `s2_analogue_data.py` | `s2_analogue_sets.json` `country:FR`, `country:CA` free to read: 73.2 vs 59.2 (2020) |
| French bronze drop at the 2023/2024 boundary | *not in these scripts*; checked 23 Nov 2026 | French papers free without a licence, 17.0% (2023) to 4.2% (2025), most of the step at one publisher |

## What if we'd borrowed someone else's design? and Where would the papers live?

| Number | Script | File and field |
| --- | --- | --- |
| Middle estimates for all Canadian papers in 2030: 74% to 79% | `s5_projection_paths.py` | `projections.json` `scenarios[].national.2030[2]`: 74.4 (2026 policy, no checks) to 78.7 (UK-style) |
| UK-style about +4 points (77% to 80%) | `s5_projection_paths.py` | `uk_ref.national.2030` = 76.9, 80.5, 78.7 |
| 2026 policy with checks adds less than a point; 2025 draft a little more | `s5_projection_paths.py` | `as_written_checked.national.2030[2]` 75.1; `draft_2025_checked` 75.6 |
| Most Canadian papers have at least one author who applies for tri-agency money: 65% to 72% | `checks/applicant_share.py` | `applicant_share.json` `at_least_5` and `at_least_3` `any_canadian_author.pct`: 64.5, 71.6 |
| Gold and hybrid 18% (2016) to 53% (2025) of Canadian papers; repository-only 13% to 9% | `s1_canada_sets.py` | `s1_canada_sets.json` `canada.routes`: `(gold + hybrid) / n` 18.2, 52.6; `green / n` 13.3, 8.6 |
| Open copies in Canada: 9% (no checks), 25% (checks), 34% (2025 draft), 37% (Netherlands-style), 48% (France-style), 53% (UK-style), 83% (US-style, 77% to 89%) | `s5_projection_paths.py` | `projections.json` `scenarios[].home.2030` |
| US-style with Canada's grant-date start: about 35% | *not in these scripts*; `s5_projection_paths.py` with the US line's coverage set to the phase-in `P` instead of `COV` | 35% |
| Measured line about 7% to 8% (2016-2024), 5.7% in 2025 | `s1b_open_copies.py` | `s1b_open_copies.json` `pct_open_copy` |
| Records fell much more since 2019 | `s1b_open_copies.py` | `pct_record`: 15.6 (2019) to 8.7 (2025) |
| 2025 draft gap mostly timing | *not in these scripts*; `s5_projection_paths.py` with the draft's start and its preprint bump varied separately | final policy 24.6%; timing alone 32.0%; preprint bump alone 26.1%; both 34.1% |

## Should this have been a tri-agency policy at all? and So why didn't we go with these?

| Number | Script | File and field |
| --- | --- | --- |
| Canada 14th of 16 (74.3%); US 70.5%, South Korea 59.3% | `s2_analogue_data.py` | `s2_analogue_sets.json` `country:*` 2025 free to read |
| Between 12th and 15th on other ways of counting | *not in these scripts*; checked 23 Nov 2026 | the same 16 countries ranked without bronze, without green-only, publisher routes only, without preprint-only, any repository copy |
| Median Canadian university has a record of about 1.5% of its 2024-25 articles in its own repository; Polytechnique Montréal 98% | `checks/university_own_repository.csv` (OpenAlex snapshot, see `README.md`) | median of `pct_with_record_in_own_repository` 1.54; Polytechnique Montréal 97.59 |
| PubMed Central Canada: about 4% of CIHR-funded manuscripts | *not in these scripts* | CIHR's 2018 notice (linked in the post) |
| Five big publishers: about 40% of 2025 journal articles with a known publisher worldwide; about 55% of Canadian-authored; Canadian Science Publishing under 1% | *not in these scripts*; from a separate analysis of publisher concentration in OpenAlex (articles, 22 Nov 2026) | Elsevier P4310320990, Springer Nature P4310319965, Wiley P4310320595, Taylor & Francis P4310320547, Sage P4310320017 through `primary_location.source.publisher_lineage`: 39.1% worldwide, 55.0% Canadian-authored; Canadian Science Publishing P4310312929 0.9% |

## How I did it

| Number | Script | File and field |
| --- | --- | --- |
| About 5% of Canadian papers whose only free copy is a submitted version | *not in these scripts*; checked 23 Nov 2026 | 6,511 Canadian 2025 papers (5.3%) |
| Between half and two-thirds of the papers the repositories hold a record of have an open copy there | `s1b_open_copies.py` | `with_open_copy / with_record`: 51% (2016) to 66% (2025) |
| About 60% of sampled papers (2023-2025) had a grant number with a readable year | `s1_phasein.py` | `s1_phasein_lags.json` `parsed / sampled` |
| Funder links added between 22 and 23 November (9% more 2014 papers; a third more for SSHRC) | *not in these scripts*; the same counts on both days | tri-agency × Canada 2014: 21,532 to 23,554; SSHRC × Canada 2014: 1,157 to 1,540 |
