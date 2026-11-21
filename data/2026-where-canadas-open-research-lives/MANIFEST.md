# Manifest: which script makes which number

Every chart and number in the post, the script that makes it, and where it lands. Run the scripts from this folder (`python3 scripts/X.py`) with `OPENALEX_API_KEY` set. Python 3.9+, standard library only (`make_figure.py` also needs matplotlib). "Latest year" is 2025. Shares are `100 × column / n`; "free to read" is `n − closed`.

## Run order

| Step | Command | Writes | Time |
| --- | --- | --- | --- |
| 1 | `python3 scripts/build_monitor.py` | `results/routes_by_year.csv`, `grant_numbers_by_year.csv`, `closed_by_publisher.csv`, `open_by_field.csv`, `funders.csv`, `kpi_comparison.csv`, `canadian_repositories.csv`, `monitor_data.json`; `monitor.html` | ~90 s |
| 2 | `python3 scripts/make_figure.py` | `figure.png` (from `routes_by_year.csv`) | seconds |
| 3 | `python3 scripts/build_trends.py` | `results/oa_by_university.csv`, `oa_by_province.csv`, `oa_by_country.csv`, `trends_data.json`; `trends.html` | ~60 s |
| 4 | `python3 scripts/universities.py` (optional, not used in the post) | `results/university_oa_by_year.csv`, `policy_event_tests.csv` (reads `policy_timeline.csv`) | ~30 s |

`python3 scripts/build_trends.py --from-json` rebuilds `trends.html` from `trends_data.json` without calling the API.

## Post section to file

| Post section | Number or chart | Script | File and field |
| --- | --- | --- | --- |
| Top | The monitor (embedded) | `build_monitor.py` | `monitor.html` (data inlined from `monitor_data.json`) |
| Top | Card and share image: 84% free to read, 8% in a Canadian repository | `make_figure.py` | `figure.png`; `routes_by_year.csv` rows `set=tri` |
| Most Canadian research is already free to read | 84% of 2025 tri-agency papers | `build_monitor.py` | `routes_by_year.csv` `set=tri, y=2025`: `(n − closed) / n` = 27,725 / 33,095 |
| | 74% of all Canadian research | `build_monitor.py` | `routes_by_year.csv` `set=canada, y=2025`: 91,274 / 122,889 |
| Almost none of it lives where the policy will ask | About 8% with a Canadian repository copy | `build_monitor.py` | `routes_by_year.csv` `set=tri, y=2025`: `carepo / n` = 2,779 / 33,095 |
| | Fall since 2019 | `build_monitor.py` | `routes_by_year.csv` `set=tri`, `carepo / n` by year |
| | Scholaris audit (26 repositories, about 595,000 records, 195 to 242 of 392 known deposits) | not in these scripts | OpenAlex's September 2026 harvest audit for the Scholaris community |
| | U15 mean of 4.2% in own repositories | not in these scripts | Riddle et al. (2023) |
| The way papers become open has changed | Hybrid 14% (2022) to 36% (2025) of tri-agency papers | `build_monitor.py` | `routes_by_year.csv` `set=tri`: `hybrid / n` = 4,535 / 31,319 and 11,949 / 33,095 |
| | About US$72 million APC list value | `build_monitor.py` | `monitor_data.json` `apc.usd` = 71,848,777 over `apc.n_with` = 20,257 papers |
| | Butler et al. US$27.6 million (2015-2018) | not in these scripts | Butler, Matthias, Simard, Mongeon and Haustein (2022) |
| Diamond is bigger than it looks | 9% of all Canadian research, 4% of tri-agency papers | `build_monitor.py` | `routes_by_year.csv` `y=2025` `diamond / n`: canada 11,408 / 122,889; tri 1,478 / 33,095 |
| | 13% of diamond papers list a funder in Crossref, against 55% to 59% for gold and hybrid | not in these scripts | checked separately on 19 Nov 2026 against Crossref funder deposits |
| Grant numbers are the quiet win | CIHR 58%, NSERC 53%, SSHRC 53% (2025); 30% overall in 2015 | `build_monitor.py` | `grant_numbers_by_year.csv` `award / n`: CIHR 5,512 / 9,528; NSERC 11,235 / 21,047; SSHRC 1,985 / 3,779; TRI 2015 7,915 / 26,247 |
| The closed papers sit at a handful of publishers | About 5,400 closed tri-agency papers; publishers and their policies | `build_monitor.py` | `routes_by_year.csv` `set=tri, y=2025` `closed` = 5,370; `closed_by_publisher.csv` |
| How this compares with the agencies' numbers | Ours against the agencies' 2025 baselines: Canada 74.3% vs 68.6% (about 6 points); NSERC 82.6% vs 73.0%, SSHRC 77.6% vs 72.4%, CIHR 90.5% vs 85.3% (5 to 10 points) | `build_monitor.py` | `kpi_comparison.csv` `ours`, `agency` |
| How Canada compares | Both interactive charts (embedded) | `build_trends.py` | `trends.html` (data inlined from `trends_data.json`) |
| | Universities 22% to 48% (2010) and 67% to 82% (2025), counting those with at least 200 papers that year; U15 72% to 79% (2025) | `build_trends.py` | `oa_by_university.csv` `free_to_read / papers` by `year`; `u15` column |
| | Quebec and British Columbia led most years to 2021; provinces within about six points in 2025 | `build_trends.py` | `oa_by_province.csv` `free_to_read / papers`: Quebec and British Columbia are the top two of the seven largest provinces each year from 2010 to 2021; in 2025 the ten provinces run from 71% (New Brunswick) to 78% (Manitoba) |
| | Canada 39% against the world's 36% (2010), seven points behind (2020), 74% against 76% (2025) | `build_trends.py` | `oa_by_country.csv` rows `code=CA` and `country=World` |
| | 43rd of the 55 countries with at least 20,000 papers in 2025 | `build_trends.py` | `oa_by_country.csv` `year=2025`, countries with `papers ≥ 20000`, ranked by `free_to_read / papers` |
| | Hybrid up 7 points in Canada in 2024, against 3 in the United States | not saved by these scripts | check in a browser: Canada [2023](https://api.openalex.org/works?filter=type:article%7Creview,publication_year:2023,institutions.country_code:CA&group_by=oa_status) and [2024](https://api.openalex.org/works?filter=type:article%7Creview,publication_year:2024,institutions.country_code:CA&group_by=oa_status) (16.8% to 23.8%); United States [2023](https://api.openalex.org/works?filter=type:article%7Creview,publication_year:2023,institutions.country_code:US&group_by=oa_status) and [2024](https://api.openalex.org/works?filter=type:article%7Creview,publication_year:2024,institutions.country_code:US&group_by=oa_status) (13.4% to 16.5%) |
| | University policies showed no clear signal | `universities.py` | `policy_event_tests.csv`; events in `policy_timeline.csv` |
