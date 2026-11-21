"""Universities: open access by year and route, set against each university's own policies and national moves.

Standard library only. Uses OPENALEX_API_KEY if set. Run from the data folder:

    python3 scripts/universities.py

Reads results/policy_timeline.csv (sourced policy events; rows with `tested` set are tested) and writes:
  results/university_oa_by_year.csv   journal articles per university and year, by OA route, plus Canadian repository copies
  results/policy_event_tests.csv      before/after test of each dated university event against the national trend
"""
import csv
import json
import os
import statistics
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
KEY = os.environ.get("OPENALEX_API_KEY")
ROUTES = ["gold", "diamond", "hybrid", "green", "bronze", "closed"]
BASE = "type:article,primary_location.source.type:journal,publication_year:2010-2025"
WINDOW = 3  # years before and after an event

UNIVERSITIES = {  # OpenAlex institution IDs; the first 15 are the U15
    "University of Toronto": "I185261750", "University of British Columbia": "I141945490", "McGill University": "I5023651",
    "University of Alberta": "I154425047", "University of Calgary": "I168635309", "Université de Montréal": "I70931966",
    "McMaster University": "I98251732", "Western University": "I125749732", "University of Ottawa": "I153718931",
    "University of Waterloo": "I151746483", "Université Laval": "I43406934", "Queen's University": "I204722609",
    "University of Manitoba": "I46247651", "Dalhousie University": "I129902397", "University of Saskatchewan": "I32625721",
    "Simon Fraser University": "I18014758", "York University": "I192455969", "Concordia University": "I60158472",
    "University of Guelph": "I79817857", "University of Victoria": "I212119943", "Carleton University": "I67031392",
    "Université de Sherbrooke": "I135117807", "Université du Québec à Montréal": "I159129438",
    "Memorial University of Newfoundland": "I130438778", "Toronto Metropolitan University": "I530967",
    "University of Windsor": "I74413500", "Institut National de la Recherche Scientifique": "I39481719",
    "Polytechnique Montréal": "I45683168", "École de Technologie Supérieure": "I9736820", "Wilfrid Laurier University": "I75381157",
}
U15 = list(UNIVERSITIES)[:15]


def get(path, **params):
    if KEY:
        params["api_key"] = KEY
    url = "https://api.openalex.org/" + path + "?" + urllib.parse.urlencode(params, safe=":,|!<>")
    for attempt in range(6):
        try:
            with urllib.request.urlopen(url, timeout=90) as r:
                return json.load(r)
        except Exception as e:
            err = e
            time.sleep(2 * (attempt + 1))
    raise err


def by_year_route(f):
    out = {}
    for g in get("works", filter=f, group_by="publication_year,oa_status")["group_by"]:
        out[int(g["key"])] = {**{s["key"]: s["count"] for s in g["groups"]}, "n": g["count"]}
    return out


def by_year(f):
    return {int(g["key"]): g["count"] for g in get("works", filter=f, group_by="publication_year")["group_by"]}


def fetch():
    repos = [r["id"].rsplit("/", 1)[-1] for r in csv.DictReader(open(RESULTS / "canadian_repositories.csv"))]
    carepo = "locations.source.id:" + "|".join(repos)
    rows = []
    sets = {"Canada": "institutions.country_code:CA", **{n: f"authorships.institutions.lineage:{i}" for n, i in UNIVERSITIES.items()}}
    for name, f in sets.items():
        yr = by_year_route(f"{BASE},{f}")
        rep = by_year(f"{BASE},{f},{carepo}")
        for y in range(2010, 2026):
            d = yr.get(y, {"n": 0})
            rows.append({"entity": name, "u15": name in U15, "year": y, "n": d["n"], **{r: d.get(r, 0) for r in ROUTES},
                         "canadian_repository": rep.get(y, 0)})
    with open(RESULTS / "university_oa_by_year.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["entity", "u15", "year", "n"] + ROUTES + ["canadian_repository"])
        w.writeheader()
        w.writerows(rows)
    return rows


def share(rows, entity, year, measure):
    r = next(x for x in rows if x["entity"] == entity and int(x["year"]) == year)
    n = int(r["n"])
    if not n:
        return None
    if measure == "open":
        return 100 * (n - int(r["closed"])) / n
    if measure == "green":
        return 100 * int(r["green"]) / n
    if measure == "gold":
        return 100 * int(r["gold"]) / n
    raise ValueError(measure)


def excess_change(rows, entity, year, measure):
    """Mean share in the (up to) 3 years after the event minus the 3 years before, net of the same change for Canada.
    Needs at least 2 years on each side inside 2010-2025."""
    pre = [y for y in range(year - WINDOW, year) if y >= 2010]
    post = [y for y in range(year + 1, year + 1 + WINDOW) if y <= 2025]
    if len(pre) < 2 or len(post) < 2:
        return None
    def mean(e, ys):
        return statistics.mean(share(rows, e, y, measure) for y in ys)
    return (mean(entity, post) - mean(entity, pre)) - (mean("Canada", post) - mean("Canada", pre))


def test_events(rows):
    """Test each tested event (results/policy_timeline.csv, column `tested`) against the national trend, and rank it
    against the same change at the other 29 universities in the same years (1 = largest gain)."""
    tests = []
    for e in csv.DictReader(open(RESULTS / "policy_timeline.csv", encoding="utf-8")):
        if not e["tested"] or e["university"] not in UNIVERSITIES:
            continue
        if e["tested"] == "institution-wide policy":
            events = [("policy adopted", int(e["start_year"]), "green")]
        else:
            events = [("APC fund opens", int(e["start_year"]), "gold")]
            if e["end_year"].isdigit():
                events.append(("APC fund closes", int(e["end_year"]), "gold"))
        for label, year, main in events:
            for measure in (main, "open"):
                mine = excess_change(rows, e["university"], year, measure)
                if mine is None:
                    continue
                others = [excess_change(rows, u, year, measure) for u in UNIVERSITIES if u != e["university"]]
                tests.append({"university": e["university"], "event": label, "year": year, "measure": measure,
                              "excess_change_pts": round(mine, 1), "rank_of_30": 1 + sum(o >= mine for o in others),
                              "median_other_pts": round(statistics.median(others), 1),
                              "description": e["description"], "source_url": e["source_url"]})
    with open(RESULTS / "policy_event_tests.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(tests[0]))
        w.writeheader()
        w.writerows(tests)
    return tests


if __name__ == "__main__":
    rows = fetch()
    rows = list(csv.DictReader(open(RESULTS / "university_oa_by_year.csv")))
    for r in test_events(rows):
        print(r["university"], r["event"], r["year"], r["measure"], r["excess_change_pts"], f"rank {r['rank_of_30']}/30")
