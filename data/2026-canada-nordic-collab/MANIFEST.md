# Manifest: which script makes which number

Every number and chart in the post, the script that makes it, and where it lands in `results/`. Run scripts from `scripts/` (`cd scripts; python3 X.py`); `OPENALEX_API_KEY` is optional. Python 3.9+, standard library only. `post_numbers.py` recomputes every OpenAlex number below from the saved files and writes them to `post_numbers.json` (keys in the last column, after "pn:").

## Run order

| Step | Command | Writes (in `results/`) |
| --- | --- | --- |
| 1 | `python3 pull_pairs.py` | `pairs.json` |
| 2 | `python3 pull_context.py` | `context.json` |
| 3 | `python3 pull_arctic.py` | `arctic.json` |
| 4 | `python3 pull_subfields.py` | `subfields.json` |
| 5 | `python3 pull_priorities.py` | `priorities.json` |
| 6 | `python3 pull_institutions.py` | `institutions.json` |
| 7 | `python3 pull_open.py` | `open.json` |
| 8 | `python3 check_arctic.py` | `check_arctic.json` (+ local title samples in `cache/`) |
| 9 | `python3 check_programmes.py` | `check_programmes.json` |
| 10 | `python3 chart_data.py` | `chart_shares_rows.json`, `chart_arctic_vs_all_rows.json`, `chart_priorities_rows.json` |
| 11 | `python3 post_numbers.py` | `post_numbers.json` |

## Post section to file

Shares are out of every 100 Canadian articles unless the post says otherwise. `pairs.CA.<year>.<cc>` is the number of Canadian articles with a co-author in country `cc`; `pairs.CA.<year>.CA` is all Canadian articles. `nordic_union.<year>._with_CA` counts Canada–Nordic articles once.

| Post section | Number or chart | Script | File and field |
| --- | --- | --- | --- |
| Short version | 5 in 100 in 2025, about three times 2000; growth in step with other European ties | `pull_pairs.py` | as in the next section; pn: `canada_side.nordic_share_2000/2025`, `x_since_2000` |
| | 16% of Arctic articles, three times the overall rate | `pull_arctic.py`, `pull_pairs.py` | `arctic.json` `by_group.CA.2025._with_NORDIC / _total`; pn: `arctic_canada.2025`, `arctic_vs_all_2025_ratio` |
| | Quantum, AI, connectivity, clean energy, space technology at 2 to 3 in 100; overall 3.9 | `pull_priorities.py` | `priorities.json` `<area>.2021-2025.CA_NORDIC_le10 / CA_le10`; pn: `priority_areas_2021_2025.<area>.canada_side_le10` |
| Why now? | 28 government texts; Arctic security 14, Indigenous and northern communities 13, AI and supercomputing 13, Arctic and polar research 12, critical minerals 12, quantum 11, climate 10, clean energy 10; quantum and space from 2025 | hand count | `policy_texts.md` (not made by a script) |
| How much already? | Chart 1: share of Canadian articles with a co-author in the Nordic countries, UK, Germany, France, Australia, Netherlands, 2000-2025; US 24.6%, China 10.1% in the notes | `pull_pairs.py`, `chart_data.py` | `chart_shares_rows.json`; `pairs.json` `pairs.CA.<year>.<cc>`, `nordic_union.<year>._with_CA` |
| | 5,678 articles (5.0%) in 2025; 1.5% in 2000 | `pull_pairs.py` | `nordic_union.2025._with_CA`, `pairs.CA.2025.CA`; pn: `canada_side` |
| | Seventh-largest partner; Australia 5.4%, France 6.0%, Germany 6.3%, US 24.6%, China 10.1%, UK 9.5%; Sweden 2.3% | `pull_pairs.py` | `pairs.CA.2025.<cc>`; pn: `canada_side.partners_2025_top10`, `nordic_rank_2025`, `nordic_countries_2025.SE` |
| | UK and Germany shares roughly tripled | `pull_pairs.py` | pn: `canada_side.x_since_2000` (UK 2.86, Germany 2.93) |
| | 30% (2000) and 56% (2025) of Canadian articles with a co-author abroad | `pull_context.py` | `context.json` `intl.<year>` = [international, all]; pn: `canada_side.international_share` |
| | From the Nordic side, Canada 11th, 5.0%; eighth in 2000; China, Spain, Australia, Switzerland passed it | `pull_pairs.py` | `nordic_union.<year>.<cc> / _total`; pn: `nordic_side.2000`, `nordic_side.2025` |
| | Greenland 2021-2025: 26% with a Canadian co-author, second to Denmark | `pull_context.py` | `context.json` `greenland_2021_2025.CA / _total`; pn: `greenland_2021_2025` |
| | About 1 in 5 joint articles 2021-2025 have 11+ countries | `pull_subfields.py` | `subfields.json` `CA_NORDIC.total` (25,973) vs `CA_NORDIC_le10.total` (20,973); pn: `consortia.share_with_11plus_countries` |
| | Without them: 2.6 times since 2000, against 2.5 (UK) and 2.4 (Germany) | `pull_context.py` | `context.json` `le10.<year>.<cc> / _total`; pn: `consortia.le10_x_since_2000` |
| What do they work on? | Chart 2: Nordic share of Canada's Arctic and northern articles vs all Canadian articles, 2000-2025 | `pull_arctic.py`, `pull_pairs.py`, `chart_data.py` | `chart_arctic_vs_all_rows.json`; `arctic.json` `by_group.CA.<year>._with_NORDIC / _total` |
| | 16.4% of 1,259 Arctic articles in 2025; 9% in 2000; 18 to 20% in 2020-2024 | `pull_arctic.py` | `arctic.json` `by_group.CA.<year>`; pn: `arctic_canada` |
| | Canada's Arctic ties with the US, UK, Germany, France rose and fell | `pull_arctic.py` | `arctic.json` `by_group.CA.<year>.<cc> / _total`; pn: `arctic_canada.<year>.<cc>_share` |
| | Nordic Arctic articles with Russia 9.2% (2021) to 3.6% (2025); Canada 13.1% then 12.1%; Germany and China grew | `pull_arctic.py` | `arctic.json` `by_group.NORDIC.<year>.<cc> / _total`; pn: `arctic_nordic_side` |
| | Fields, 10 or fewer countries: Earth and planetary 8, physics and environmental science about 6; arts and humanities 1.1, engineering 2.2, social sciences and economics 2.3 each thinnest | `pull_subfields.py` | `subfields.json` `CA_NORDIC_le10.field.<id> / CA_le10.field.<id>`; pn: `fields_le10` (all papers: `fields_all_papers`) |
| | Institutions: Toronto, UBC, McGill; Copenhagen, Karolinska, Oslo; for the North, Environment and Climate Change Canada, Manitoba, Fisheries and Oceans; Aarhus, UiT, Copenhagen (top three by joint Arctic articles) | `pull_institutions.py` | `institutions.json` `all|arctic.by_country.<cc>.institutions` ([id, name, articles, country, type]); pn: `institutions_top3` |
| Room to grow? | Chart 3: 14 priority areas, 2021-2025, 10 or fewer countries; reference 3.9 | `pull_priorities.py`, `chart_data.py` | `chart_priorities_rows.json`; `priorities.json` `<area>.2021-2025.CA_NORDIC_le10 / CA_le10`, `all` for the reference |
| | Space science 17.5, Arctic 17.1, oceans 10.2, climate 9.4; space technology 2.0, quantum 2.6, connectivity 2.6, AI 2.8, clean energy 3.0; mining 3.9, mineral geology 5.2; Indigenous 2.1 | `pull_priorities.py` | as above; pn: `priority_areas_2021_2025.<area>.canada_side_le10`, `x_overall_rate` |
| | All but space and satellite technology low from the Nordic side too | `pull_priorities.py` | `<area>.2021-2025.CA_NORDIC_le10 / NORDIC_le10`; pn: `priority_areas_2021_2025.<area>.nordic_side_le10` |
| | Quantum joint articles 34 (2016-2020), 36 (2021-2025); Canada's quantum output up about a quarter | `pull_priorities.py` | `quantum.<period>.CA_NORDIC`, `quantum.<period>.CA`; pn: `priority_areas_2021_2025.quantum` |
| | Canada publishes about 19% of the world's Indigenous-topic articles; 15 in 100 Nordic articles in them have a Canadian co-author | `pull_priorities.py` | `indigenous.2021-2025.CA / world`, `CA_NORDIC / NORDIC`; pn: `priority_areas_2021_2025.indigenous` |
| | NordForsk credited on 138 joint articles, 2016-2025 | `check_programmes.py` | `check_programmes.json` `nordforsk_on_joint.NordForsk` (funder F4320322885) |
| | NSERC, European Commission, CIHR, Swedish Research Council (Vetenskapsrådet) above all | `pull_institutions.py` | `institutions.json` `all.funders_le10`; pn: `funders_on_joint_2021_2025_le10_top6` |
| Open infrastructure | 89 to 92% of 2024 articles free to read in Finland, Norway, Sweden; 84% Denmark; 81% Iceland; 74% Canada; the gap is mostly open access at the publisher | `pull_open.py` | `open.json` `<cc>.total`, `oa_status` (free to read = total minus `closed`); pn: `free_to_read_2024` |
| What none of this can tell us | The Nordic countries publish 17% of the world's Arctic articles | `pull_arctic.py` | `arctic.json` `by_group.NORDIC.<year>._total / by_group.WORLD.<year>._total`; pn: `nordic_share_of_world_arctic` (16.9% for 2021-2025, 17.6% for 2016-2025) |

## Inputs that are not made by a script

- `policy_texts.md`: the 28 government texts (2017 to 2026) and which of them name each priority, read by hand. Each text is linked there.
- Facts about national research information systems, CoARA membership, PKP funding, conferences and the tri-agency policy come from the pages linked in the post's "How do they compare on open research infrastructure?" section.
