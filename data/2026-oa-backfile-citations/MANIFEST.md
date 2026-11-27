# Manifest: which script makes which number

Every number and chart in the post, the script that makes it, and where it lands. Run order is in `README.md`. Percentages are changes in yearly citations to opened papers against matched closed papers (`pct` fields = 100 × (e^b − 1)). "Pure set" = the 113 openings in the headline (`status pure` in `results/v3/final_events_v3.tsv`).

The JSON result files are lists of entries. An entry is named here by its fields, for example `estimands.json` [item `main`, set `PURE v3`, weight `citation-weighted`]. In those entries `pct` is the estimate, `boot_lo95` / `boot_hi95` / `boot_p_zero` the bootstrap interval and p-value over program-date groups, `src_lo95` / `src_hi95` (or `lo95` / `hi95` where `cluster` is `src`) the interval over journals, and `mde80_crv_t` / `mde80_boot` the smallest effect the design would detect 80% of the time.

## Numbers computed here

| Post section | Number or chart | Script | File and field |
| --- | --- | --- | --- |
| Short version; How I looked | 113 openings, 2005 to 2024 | `v3_events.py`, `v3_extras.py` | `results/v3/extras.json` [item `counts`] `openings` (113), `T_min` (2005), `T_max` (2024) |
| | About 346,000 papers | `v3_extras.py` | same entry, `papers` (346,011) |
| | Between 2% and 7.5%; about 2%, about 4%, about 7.5% | `v3_estimands.py` | `results/v3/estimands.json` [item `main`, set `PURE v3`]: weight `citation-weighted` `pct` 1.93; `article-weighted` 4.40; `event-weighted` 7.50 |
| | Can't reliably detect effects smaller than about 8 to 11% | `v3_estimands.py` | same, citation-weighted: `mde80_crv_t` 7.6, `mde80_boot` 11.1 |
| How I looked | Programs: Elsevier mathematics 2012, archive joiners, AMS 2010, Cell Press 2005, Royal Society 2011, one single journal | `v3_extras.py` | `extras.json` [item `counts`] `by_program` (53, 36, 5, 9, 9 and 1 openings) |
| | Openings that didn't last were dropped | `v3_events.py` | `results/v3/final_events_v3.tsv` `v3_status` `dropped`, `v3_reason` "opening did not hold" (3 journals) |
| | Up to five comparison journals | `v3_estimands.py` (matching) | `extras.json` [item `counts`] `five_controls` (108 of 113); `results/v3/stacks_v3.tsv` `controls` |
| Chart 1 | Rows (opened / similar closed, years −5 to +8) | `v3_extras.py` | `results/v3/chart1_raw_balanced.json` `k`, `opened`, `control` (same rows in `extras.json` [item `chart1`]) |
| | 97 openings; 289,830 papers | `v3_extras.py` | `chart1_raw_balanced.json` `n_openings`, `articles`. The 97 opened from 2005 to 2016 (`stacks_v3.tsv`, pure, `T` + 8 ≤ 2025) |
| | Largest gap after opening: 1.5 points | computed from the rows | year +1: 99.1 vs 100.6 |
| | About a third of year −1 citations went to papers from the last five years (35% opened, 30% comparison) | `v3_extras.py` | `chart1_raw_balanced.json` `share_minus1_cites_from_papers_published_T_minus_5_to_T_minus_1` (0.349, 0.302) |
| | Back files ran up to about 4 years before the opening | `v3_extras.py` | `extras.json` [item `counts`] `median_T_minus_hi` (4) |
| Model paragraph | Roughly −4% to +12% (citation-weighted) | `v3_estimands.py` | `estimands.json` [item `main`, set `PURE v3`, weight `citation-weighted`] `boot_lo95` −3.6, `boot_hi95` 11.7, `boot_p_zero` 0.44 |
| | Top of the range about 12% weighting by papers; about 23% counting each opening equally | `v3_estimands.py` | same set: `article-weighted` `boot_hi95` 12.5 (p 0.09); `event-weighted` `boot_lo95` −0.2, `boot_hi95` 22.6 (p 0.055) |
| | About 50 Elsevier mathematics journals opened on one date in 2012 | `v3_extras.py` | `extras.json` [item `counts`] `by_program` `Elsevier maths open archive 2012` `n` (53) |
| Which programs drive it | Without Cell Press about 4.5%, clearly above zero | `v3_estimands.py` | `estimands.json` [item `no Cell Press`, weight `citation-weighted`] `pct` 4.54, `boot_lo95` 1.4, `boot_hi95` 14.5, `boot_p_zero` 0.005 |
| | Without the Elsevier archive joiners about zero | `v3_estimands.py` | `estimands.json` [item `leave one out`, set `PURE v3 leave out: Elsevier open archive join`, weight `citation-weighted`] `pct` −0.01 |
| Annual Reviews check | Opened volumes did no better than closed ones (−1.3%) | `estimate_within.py` (first panel, `q08`) | `results/estimates_within.json` [label `WITHIN: Annual Reviews 2023 ...`] `pct` −1.28 (−4.4 to +2.0), 37 journals |
| Assumptions and caveats | 2.5% had an arXiv copy before the opening | `v3_arxiv_share.py` | `results/v3/arxiv_share.json` `share_arxiv_before_T` (8,783 of 352,540; the uncleaned Q10 panel) |
| | Those gained no less than the rest | `v2_prior_citing.py` | `results/v2/prior_citing.json` [item 5, split `arXiv copy posted before T`] vs [split `no arXiv copy before T`]; difference entry [item 5, note `difference arXiv-before-T minus none`] `b` +0.027 (se 0.025). Not rerun on v3 |
| | 58 of 113 openings, 62% of the papers, from two mathematics programs | `v3_extras.py` | `extras.json` [item `maths shares`] `maths_programs` 58, `maths_programs_papers` 213,666 of `papers` 346,011 |
| | Without them about 1.5%, or 9.5% counting each opening equally | `v3_extras.py` | `extras.json` [item `maths`, set `PURE v3 no maths programs or maths journals`] citation `pct` 1.48 (bootstrap −6.0 to +17.3), event `pct` 9.47 |
| | Reference lists missing for roughly one in eight citing papers; within about 2 points every year 1995 to 2025; lower for opened journals after 2016 | `v3_make_q14.py` + `v3_q14_citing_pool_coverage.sql` | `data/v3_q14_coverage.json` `cov_ref_weighted` by `pool` and `cy`: missing share 13.4% (opened) and 12.8% (comparison) weighted by citations, 6% to 18% by year; gap opened minus comparison +0.4 to +2.1 points 1995-2006, within ±0.5 2007-2015, −0.2 to −2.2 2016-2025 |
| Sci-Hub paragraph | Openings with fewer prior citations gained more (about 7.5% counting each opening equally) than the most-cited ones (about 2%) | `v3_estimands.py` | the event-weighted and citation-weighted `main` entries above |
| What none of this can tell us | Papers opened within five years of publication: about 1.4% (−3% to +6%) | `v3_extras.py` | `extras.json` [item `age`, set `PURE v3 papers 1-5 years old at opening`, weight `citation-weighted`] `pct` 1.42, `lo95` −3.3, `hi95` +6.4 (96 openings, 20% of papers) |
| | About 5 in 100 opened papers freed within two years of publication | `v4_counts.py` | `results/v4_recent/counts.json` `pure` `papers_age2` 16,044 of `papers_opened` 346,011 (4.6%; no pure opening freed 1-year-old papers); with flips and Subscribe to Open, `all flips and S2O` `papers_age1_2` 4,478 of 55,496: 20,522 of 401,507 (5.1%) |
| | They don't seem to have gained either | `v4_followup.py` | `results/v4_recent/followup2.json` [item `RVP`, set `RVP pure age 2, REAL MINUS PLACEBO`, weight `citation-weighted`] `pct` −4.0, `boot_lo95` −15.6, `boot_hi95` +10.6; event-weighted −3.0 |
| | Too few to rule out a gain of 10 to 20% | `v4_followup.py` | same entry: `mde80_src` 11.4, `mde80_boot` 21.3 |
| | Effects smaller than about 8 to 11% | `v3_estimands.py` | as in the short version |
| How I did it | 49 openings with two date sources give about 1% | `v3_extras.py` | `extras.json` [item `counts`] `two_date_sources` 49; [item `two sources`, weight `citation-weighted`] `pct` 1.13 |
| | Openings set aside, with reasons | `final_events.py`, `v3_events.py` | `results/final_exclusions.tsv` `reason`; `final_events_v3.tsv` `v3_reason` |
| | Journal articles only, each counted once: about 1%, or about 5.5% counting each opening equally | `v3_extras.py` | `extras.json` [item `citing`, set `PURE v3 \| journal articles citing, each counted once`] citation `pct` 0.88, event `pct` 5.60 |
| | Citations from repository papers rose about 11% | `v3_extras.py` | `extras.json` [item `citing`, set `PURE v3 \| repository-only citers`, weight `citation-weighted`] `pct` 10.59 |
| | 14 groups of openings that shared a date | `v3_estimands.py` | `extras.json` [item `counts`] `G` (14); `stacks_v3.tsv` `pd` |
| | Fake opening three years early: about +1% (−1% to +3%) | `v3_extras.py` | `extras.json` [item `placebo`] `pct` 0.93, `lo95` −1.0, `hi95` +2.9 |
| | Snapshot of 22 November 2026 | `v3_make_q12.py` | the Q12 panel; `work_citations` built 2026-11-22 12:11 UTC |

## From the literature, not computed here

| Post section | Number | Source |
| --- | --- | --- |
| Intro | Open access advantage of about 18% (open papers against the average paper of the same age and field) | The state of OA, PeerJ 2018, [doi 10.7717/peerj.4375](https://doi.org/10.7717/peerj.4375), [OpenAlex W2741809807](https://openalex.org/W2741809807) |
| Intro | Earlier study of publishers' back-file openings | Economic Inquiry 2014, [doi 10.1111/ecin.12064](https://doi.org/10.1111/ecin.12064), [OpenAlex W3121567788](https://openalex.org/W3121567788) |
| Losing access; chart 2 | About 400,000 articles 2012-2020; Elsevier's share of references to recent papers 23.4% (2012), 25.0% (2018), 24.0% (2020); citations to Elsevier 77,542 (2016) to 93,035 (2020); Elsevier's share of their articles 26.3% (2015) to 20.8% (2020); yearly rows in chart 2 | No deal, Quantitative Science Studies 2023, [doi 10.1162/qss_a_00255](https://doi.org/10.1162/qss_a_00255), [OpenAlex W4362696813](https://openalex.org/W4362696813), and its published data, [doi 10.5281/zenodo.7439093](https://doi.org/10.5281/zenodo.7439093) |
| Losing access | About 180 institutions cut off in July 2018, about 25 more in January 2019; new agreement signed September 2023 | the same study; the agreement date from Projekt DEAL's announcement |
| Losing access | Trial 1: downloads up 89%, free articles not cited more after a year | BMJ 2008, [doi 10.1136/bmj.a568](https://doi.org/10.1136/bmj.a568), [OpenAlex W1970217003](https://openalex.org/W1970217003) |
| Losing access | Trial 2: 36 journals, no more citations within three years | FASEB Journal 2011, [doi 10.1096/fj.11-183988](https://doi.org/10.1096/fj.11-183988), [OpenAlex W2160597895](https://openalex.org/W2160597895) |
| Reading; chart 3 | 70-90% of citations copied from other reference lists (model estimate) | Scientometrics 2005, [doi 10.1007/s11192-005-0028-2](https://doi.org/10.1007/s11192-005-0028-2), [OpenAlex W1968815786](https://openalex.org/W1968815786) |
| Reading; chart 3 | 9,380 authors, 17,154 citations, 54% little or no influence | Research Policy 2022, [doi 10.1016/j.respol.2022.104484](https://doi.org/10.1016/j.respol.2022.104484), [OpenAlex W4206622121](https://openalex.org/W4206622121) |
| Reading; chart 3 | 16.9% to 25.4% of citations in medical journals misstate the source | PeerJ 2015, [doi 10.7717/peerj.1364](https://doi.org/10.7717/peerj.1364), [OpenAlex W1847240671](https://openalex.org/W1847240671); Research Integrity and Peer Review 2025, [doi 10.1186/s41073-025-00173-z](https://doi.org/10.1186/s41073-025-00173-z), [OpenAlex W4412565252](https://openalex.org/W4412565252) |
| Reading; chart 3 | Of 13,252 citations to retracted papers in biomedicine, 5.4% mention the retraction | Quantitative Science Studies 2021, [doi 10.1162/qss_a_00155](https://doi.org/10.1162/qss_a_00155), [OpenAlex W4200394820](https://openalex.org/W4200394820) |
| Reading | Sci-Hub use raised the share of references to paywalled papers by about 7% (5 points, +7.4%) | Leveling the playing field, working paper 2025, now a chapter of a 2026 dissertation, [OpenAlex W7161360389](https://openalex.org/W7161360389) |
| Caveats | Sci-Hub around since 2011 | the same working paper |

## Charts

Chart 1 is drawn from `results/v3/chart1_raw_balanced.json`. Charts 2 and 3 are typed from the papers in the table above. `figures/*.png` are renders of the Claude Docs chart modules in `figures/*.jsx`; each module carries its numbers as rows, so a module is also a readable copy of its chart's data.
