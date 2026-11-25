# Who uses OpenAlex, and who pays for it? Data and scripts

The numbers and charts behind the post [Who uses OpenAlex, and who pays for it?](https://kyledemes.com/notes/2026/who-uses-openalex/). The papers come from the [OpenAlex API](https://docs.openalex.org) (CC0), pulled on 24 November 2026. OpenAlex's own funding comes from its public grant announcements, its [supporters page](https://openalex.org/institutional-supporters) and its [US tax filing](https://projects.propublica.org/nonprofits/organizations/461599252). `MANIFEST.md` maps every number and chart in the post to its script and file.

## Run order

```
export OPENALEX_API_KEY=...                  # recommended: without a key, paging stops at 10,000 results
cd scripts
python3 pull_candidates.py                   # works that say "openalex" or cite the OpenAlex paper (~75 requests)
python3 denominators.py                      # all research papers 2022-2026 by country, field, year, funder (9 requests)
python3 fetch_passages.py 32                 # open copies of works that don't name OpenAlex in the abstract (~1 hour)
python3 classify.py titleabs                 # label works that name OpenAlex in the title or abstract
python3 classify.py fulltext                 # label the rest from the passages around each mention
python3 classify.py late                     # relabel long abstracts that name OpenAlex after the 1,800-character cut
python3 supporters_summary.py                # paying members by country and type (needs the hand copy, below)
python3 analyse.py                           # the corpus and its breakdowns (no API calls)
python3 awards_flow.py                       # grants listed on those papers, by funder (no API calls)
python3 robustness.py                        # citation share by year, prolific-author check, the 7,500-9,000 estimate
python3 check_agreement.py --draw            # two random samples of 100 for the second-model check
CLASSIFY_MODEL=opus python3 classify.py validate ../checks/sample_titleabs.txt
CLASSIFY_MODEL=opus python3 classify.py validate ../checks/sample_body.txt
python3 check_agreement.py                   # agreement between the two models
python3 make_figures.py                      # the five charts as Claude Docs chart modules (figures/*.jsx)
```

Python 3.9 or later. Standard library only, except `fetch_passages.py`, which needs [PyMuPDF](https://pymupdf.readthedocs.io) to read PDFs, and `classify.py`, which calls the [Claude Code](https://claude.com/claude-code) command line tool (`claude -p`) with Claude Haiku 4.5 (and Claude Opus for the check). Language model labels vary a little from run to run, and OpenAlex updates daily, so a later run will differ a little.

## What's not here, and why

The scripts write two local folders that are not published:

- `data/` holds the raw API records (with author names), the passages around each mention, and one label per work.
- `checks/` holds the two random samples and the second model's label for each work in them.

Both are per-paper. Publishing a list of papers with a model's verdict on each would be a claim about named people's work, and a second model disagreed with about 3 in 100 of them. The results below are counts only. `supporters_summary.py` reads a hand copy of the supporters page (the page needs a browser), with a country and a type set for each member by hand. Thirteen members, mostly companies, had no clear country.

## What's in `results/`

| File | What it holds |
| --- | --- |
| `summary.json` | The corpus: size, how each mention sorted out (`funnel`), roles and uses, papers by year and by how they were found, types, countries (with the comparison shares), institutions, fields, funders, the citation check |
| `denominators.json` | All research papers of the same types, 2022-2026, by country, field, year and funder, all and with full text; papers with at least one author country |
| `awards_by_group.json` | Distinct grants (award records) on papers that used OpenAlex, by funder group, and the funders in the group that also pay for OpenAlex |
| `supporters.json` | OpenAlex's paying members by tier, type and country (counts only) |
| `robustness.json` | Share of users citing the OpenAlex paper by year; reviews in 2025 and 2026; 2026 against 2025 without prolific authors; the estimate and its two assumptions; full-text share |
| `agreement.json` | How often Claude Opus agreed with the labels used, on the two samples |

## Check the headline numbers in a browser

Works whose full text, title or abstract says "openalex" (9,578 on 24 November):
<https://api.openalex.org/works?filter=fulltext.search:openalex&corpus=all>

Works that say it in the title or abstract (4,749):
<https://api.openalex.org/works?filter=title_and_abstract.search:openalex&corpus=all>

Works that cite the paper describing OpenAlex (1,477):
<https://api.openalex.org/works?filter=cites:W4229010617&corpus=all>

Research papers published 2022-2026 (53.4 million):
<https://api.openalex.org/works?filter=publication_year:2022-2026,type:article|review|preprint|conference-paper|book-chapter|book|dissertation|report&corpus=all>

## Known limits

- The count is a floor. OpenAlex holds full text for 45% of research papers from these years, and 1,136 papers that name OpenAlex only in the body had no readable open copy. `robustness.json` gives the estimate (about 7,600, or about 8,900 with the lower full-text rate).
- About 70 review protocols that only plan to search OpenAlex were labelled as users, and 167 papers whose abstract the API doesn't show were judged from the title alone. Together they move the count by 1% to 3%.
- One Zenodo copy of the OpenAlex paper itself is counted as a user.
- Funders are those OpenAlex records on each paper; 22% of these papers name one, and 615 list a specific grant.
