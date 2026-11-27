# Canada and the Nordic countries: data and scripts

The numbers and charts behind the post [Canada and the Nordic countries: research ties, the North, and open infrastructure](https://kyledemes.com/notes/2026/canada-nordic-research-ties/). All counts come from the [OpenAlex API](https://docs.openalex.org) (CC0), pulled on 24 November 2026. `MANIFEST.md` maps every number and chart in the post to its script and file. `policy_texts.md` lists the 28 government texts behind the priority counts in "Why now?".

## Definitions

- **Articles**: OpenAlex `type:article`, counted by publication year.
- **Nordic**: at least one author lists an institution in Denmark, Finland, Iceland, Norway, Sweden, Greenland, the Faroe Islands or Åland (`institutions.country_code:DK|FI|IS|NO|SE|GL|FO|AX`). A Canada–Nordic article also has at least one Canadian institution, and counts once however many Nordic countries are on it.
- **Whole counting**: an article counts for every country on it.
- **Big consortia left out**: "10 or fewer countries" means `countries_distinct_count:<11`.
- **Arctic and northern**: the title or abstract matches the search in `scripts/defs.py` (`TERMS`, joined into `Q`): arctic, subarctic, Greenland, Svalbard, Nunavut, Nunavik, Nunatsiavut, Inuvialuit, Yukon, "Northwest Territories", Lapland, Barents, "Beaufort Sea", "Hudson Bay", "Fram Strait", Baffin, Finnmark, Norrbotten, Chukchi, Chukotka, Yamal, Taymyr, "Kola Peninsula", "North Slope", Saami, Sápmi, or Sami together with reindeer, Indigenous, Norway, Sweden or Finland. Three terms carry a guard: Inuit, unless the paper also names First Nations and Métis; circumpolar, unless it also names the Antarctic or the Southern Ocean; permafrost or tundra, unless it also names Tibet, Qinghai, Qilian, the Himalaya, the Tian Shan, Heilongjiang, Inner Mongolia or northeast China. Antarctic research is not included.

## Priority areas

Each article's main OpenAlex topic (`primary_topic`) decides its area, and areas can overlap (wildfire sits inside climate, for example). The Arctic and the North uses the search above. The chart's rates leave out papers with co-authors in 11 or more countries. Topic and subfield IDs as of November 2026; the same list is `AREAS` in `scripts/defs.py`.

| Area | OpenAlex definition | IDs |
| --- | --- | --- |
| The Arctic and the North | Title and abstract search (Definitions, above) | `defs.Q` |
| Climate and atmosphere | Subfields Atmospheric Science; Global and Planetary Change | subfields 1902, 2306 |
| Oceans and fisheries | Subfields Oceanography; Aquatic Science | subfields 1910, 1104 |
| Wildfire | Topic Fire effects on ecosystems | T10555 |
| Indigenous health and communities | Topics Indigenous Health, Education, and Rights; Indigenous Health and Education; Indigenous Studies and Ecology; Indigenous and Place-Based Education | T10348, T13822, T12614, T14007 |
| Mining and mineral processing | Topics Extraction and Separation Processes; Minerals Flotation and Separation Techniques; Mineral Processing and Grinding; Mining and Resource Management; Mining Techniques and Economics; Geomechanics and Mining Engineering | T11091, T11401, T12282, T11933, T13065, T13772 |
| Mineral geology and geochemistry | Topics Geochemistry and Geologic Mapping; Geochemistry and Elemental Analysis | T12157, T11740 |
| Clean energy, incl. nuclear | Subfields Renewable Energy, Sustainability and the Environment; Nuclear Energy and Engineering | subfields 2105, 2104 |
| Quantum technologies | Topics Quantum Information and Cryptography; Quantum Computing Algorithms and Architecture; Quantum optics and atomic interactions | T10020, T10682, T11414 |
| Artificial intelligence | Subfield Artificial Intelligence | subfield 1702 |
| Networks and connectivity | Subfield Computer Networks and Communications | subfield 1705 |
| Space science | Topic Ionosphere and magnetosphere dynamics | T10159 |
| Space and satellite technology | Topics Satellite Communication Systems; Space Satellite Systems and Control; Spacecraft Dynamics and Control; Spacecraft Design and Technology; Space Exploration and Technology | T12042, T11701, T11082, T12449, T14214 |
| Security and defence studies | Topics Military and Defense Studies; Defense, Military, and Policy Studies; European and Russian Geopolitical Military Strategies; European Politics and Security; Cybersecurity and Cyber Warfare Studies; Arctic and Russian Policy Studies | T14086, T12825, T13369, T14302, T12221, T12432 |

`priorities.json` also holds two rows the chart doesn't show: all articles (the 3.9 reference line) and medicine (field 27).

## Run order

```
export OPENALEX_API_KEY=...        # optional; raises the rate limit
cd scripts
python3 pull_pairs.py              # co-author countries by year, 2000-2025, for Canada, each Nordic country, comparators
python3 pull_context.py            # Canada's international share; partner shares on papers with <=10 countries; Greenland's partners
python3 pull_arctic.py             # Arctic and northern articles by partner country, 2000-2025
python3 pull_subfields.py          # articles 2021-2025 by field and subfield
python3 pull_priorities.py         # the priority areas, 2016-2020 and 2021-2025
python3 pull_institutions.py       # institutions and funders on Canada-Nordic articles, 2021-2025
python3 pull_open.py               # open access status of 2024 articles by country
python3 check_arctic.py            # Arctic set: domestic share by year
python3 check_programmes.py        # NordForsk as a funder on Canada-Nordic articles
python3 chart_data.py              # rows behind the three charts (no API calls)
python3 post_numbers.py            # every OpenAlex number in the post, recomputed (no API calls)
```

Python 3.9 or later, standard library only. `oa.py` is the shared API helper and `defs.py` holds the definitions. The pulls make about 1,700 API calls in all; `pull_arctic.py` is the slowest. OpenAlex updates daily, so a later run will differ a little.

## What's not here, and why

- `cache/`: `oa.py` saves every raw API response there, so a re-run doesn't repeat calls. It is about 90 MB and is not published.
- Two title samples from `check_arctic.py` (works that match a bare "sami", and 60 random Canadian Arctic matches read by hand) are written to `cache/` and not published: `results/` holds counts only.
- The charts were drawn as Claude Docs chart widgets from the rows in `results/chart_*_rows.json`; `figures/` holds the published images.

## What's in `results/`

| File | What it holds |
| --- | --- |
| `pairs.json` | Articles by year (2000-2025) and co-author country for Canada, each Nordic country, Greenland, the Faroe Islands and comparators; `nordic_union` treats the Nordic region as one block |
| `context.json` | Share of Canadian articles with a co-author abroad, by year; partner shares on papers with 10 or fewer countries (2000, 2010, 2020, 2025); Greenland's articles 2021-2025 by co-author country |
| `arctic.json` | Arctic and northern articles by year and co-author country, for Canada, the Nordic region, Greenland, the US, Russia, the world and core journals |
| `subfields.json` | Articles 2021-2025 by field and subfield: Canada, the Nordic region, Canada–Nordic (all and 10 or fewer countries), Canada (10 or fewer countries), the world |
| `priorities.json` | Each priority area in 2016-2020 and 2021-2025: world, Canada, Nordic, Canada–Nordic, Canada–US, and the 10-or-fewer-countries versions |
| `institutions.json` | Top institutions (per country) and funders on Canada–Nordic articles, 2021-2025, all topics and Arctic only |
| `open.json` | 2024 articles by country: open access status and copies in a repository |
| `check_arctic.json` | Canada's Arctic articles by year: total, domestic only, 10 or fewer countries, and with a Nordic co-author among those |
| `check_programmes.json` | NordForsk as a credited funder on Canada–Nordic articles, 2016-2025; Arctic Science Partnership institutions co-authoring by year |
| `chart_shares_rows.json`, `chart_arctic_vs_all_rows.json`, `chart_priorities_rows.json` | The rows drawn in charts 1, 2 and 3 |
| `post_numbers.json` | Every OpenAlex number in the post, recomputed by `post_numbers.py` |

## Check the headline numbers in a browser

Each link opens live results; the numbers in brackets are what they returned on 24 November.

- [Canadian articles in 2025, grouped by co-author country](https://api.openalex.org/works?filter=type:article,institutions.country_code:CA,publication_year:2025&group_by=institutions.country_code) (112,768; US 27,693, China 11,422, UK 10,689, Germany 7,059)
- [Canadian articles in 2025 with a Nordic co-author](https://api.openalex.org/works?filter=type:article,publication_year:2025,institutions.country_code:CA,institutions.country_code:DK%7CFI%7CIS%7CNO%7CSE%7CGL%7CFO%7CAX) (5,678)
- [Nordic articles in 2025, grouped by co-author country](https://api.openalex.org/works?filter=type:article,publication_year:2025,institutions.country_code:DK%7CFI%7CIS%7CNO%7CSE%7CGL%7CFO%7CAX&group_by=institutions.country_code) (114,299; Canada 5,678)
- [Greenland's articles, 2021 to 2025, grouped by co-author country](https://api.openalex.org/works?filter=type:article,publication_year:2021-2025,institutions.country_code:GL&group_by=institutions.country_code) (836; Canada 217)
- [Canada's Arctic and northern articles in 2025](https://api.openalex.org/works?filter=type:article,publication_year:2025,institutions.country_code:CA,title_and_abstract.search:%28arctic%20OR%20subarctic%20OR%20greenland%20OR%20svalbard%20OR%20nunavut%20OR%20nunavik%20OR%20nunatsiavut%20OR%20inuvialuit%20OR%20yukon%20OR%20%22northwest%20territories%22%20OR%20lapland%20OR%20barents%20OR%20%22beaufort%20sea%22%20OR%20%22hudson%20bay%22%20OR%20%22fram%20strait%22%20OR%20baffin%20OR%20finnmark%20OR%20norrbotten%20OR%20chukchi%20OR%20chukotka%20OR%20yamal%20OR%20taymyr%20OR%20%22kola%20peninsula%22%20OR%20%22north%20slope%22%20OR%20saami%20OR%20sapmi%20OR%20%28sami%20AND%20%28reindeer%20OR%20indigenous%20OR%20norway%20OR%20sweden%20OR%20finland%29%29%20OR%20%28inuit%20NOT%20%28%22first%20nations%22%20AND%20metis%29%29%20OR%20%28circumpolar%20NOT%20%28antarctic%20OR%20antarctica%20OR%20%22southern%20ocean%22%29%29%20OR%20%28%28permafrost%20OR%20tundra%29%20NOT%20%28tibet%20OR%20tibetan%20OR%20qinghai%20OR%20qilian%20OR%20himalaya%20OR%20himalayan%20OR%20tianshan%20OR%20%22tian%20shan%22%20OR%20%22northeast%20china%22%20OR%20heilongjiang%20OR%20%22inner%20mongolia%22%29%29%29) (1,259) and [those with a Nordic co-author](https://api.openalex.org/works?filter=type:article,publication_year:2025,institutions.country_code:CA,institutions.country_code:DK%7CFI%7CIS%7CNO%7CSE%7CGL%7CFO%7CAX,title_and_abstract.search:%28arctic%20OR%20subarctic%20OR%20greenland%20OR%20svalbard%20OR%20nunavut%20OR%20nunavik%20OR%20nunatsiavut%20OR%20inuvialuit%20OR%20yukon%20OR%20%22northwest%20territories%22%20OR%20lapland%20OR%20barents%20OR%20%22beaufort%20sea%22%20OR%20%22hudson%20bay%22%20OR%20%22fram%20strait%22%20OR%20baffin%20OR%20finnmark%20OR%20norrbotten%20OR%20chukchi%20OR%20chukotka%20OR%20yamal%20OR%20taymyr%20OR%20%22kola%20peninsula%22%20OR%20%22north%20slope%22%20OR%20saami%20OR%20sapmi%20OR%20%28sami%20AND%20%28reindeer%20OR%20indigenous%20OR%20norway%20OR%20sweden%20OR%20finland%29%29%20OR%20%28inuit%20NOT%20%28%22first%20nations%22%20AND%20metis%29%29%20OR%20%28circumpolar%20NOT%20%28antarctic%20OR%20antarctica%20OR%20%22southern%20ocean%22%29%29%20OR%20%28%28permafrost%20OR%20tundra%29%20NOT%20%28tibet%20OR%20tibetan%20OR%20qinghai%20OR%20qilian%20OR%20himalaya%20OR%20himalayan%20OR%20tianshan%20OR%20%22tian%20shan%22%20OR%20%22northeast%20china%22%20OR%20heilongjiang%20OR%20%22inner%20mongolia%22%29%29%29) (207)
- [Canadian quantum articles, 2021 to 2025, 10 or fewer countries](https://api.openalex.org/works?filter=type:article,publication_year:2021-2025,primary_topic.id:T10020%7CT10682%7CT11414,institutions.country_code:CA,countries_distinct_count:%3C11) (1,410) and [those with a Nordic co-author](https://api.openalex.org/works?filter=type:article,publication_year:2021-2025,primary_topic.id:T10020%7CT10682%7CT11414,institutions.country_code:CA,institutions.country_code:DK%7CFI%7CIS%7CNO%7CSE%7CGL%7CFO%7CAX,countries_distinct_count:%3C11) (36)
- [Canadian articles in 2024, grouped by open access status](https://api.openalex.org/works?filter=type:article,publication_year:2024,institutions.country_code:CA&group_by=oa_status) (106,535; closed 27,372)

## Reproduction check (27 November 2026)

The published scripts were run again into an empty `results/`. With the saved API responses, every results file came out identical to the 24 November files, and `chart_data.py` rebuilt the three charts' rows exactly. `pull_pairs.py` went to the live API instead: its counts were about 0.7% lower (Canadian articles in 2025: 111,969 against 112,768; with a Nordic co-author: 5,646 against 5,678), and every share quoted in the post was unchanged at the precision shown. The browser links above returned 1,261 and 207 Arctic articles, 1,412 and 36 quantum articles, and 828 Greenland articles (217 with Canada) on 27 November.

## Known limits

- The Arctic search is a keyword search on titles and abstracts. The guards remove the worst mix-ups, but some matches only mention the North in passing.
- Fields and priority areas come from each article's main OpenAlex topic, which is assigned by a model and can be wrong for single papers.
- Whole counting means big consortia count for every country on them. Rates on papers with 10 or fewer countries are given where the post uses them.
- "Free to read" counts any open copy OpenAlex finds, so it runs higher than the tri-agency figure, which uses a different method.
