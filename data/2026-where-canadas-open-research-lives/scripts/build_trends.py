"""Build the two trend charts: open access by Canadian university and province, and by country, 2010-2026.

Standard library only. Set OPENALEX_API_KEY in the environment if you have one (recommended; the
script makes about 120 requests). Run from this folder:

    python3 scripts/build_trends.py
    python3 scripts/build_trends.py --from-json   # rebuild trends.html from results/trends_data.json, no requests

Writes results/oa_by_university.csv, results/oa_by_province.csv, results/oa_by_country.csv,
results/trends_data.json, and trends.html (built from scripts/trends_template.html with the data inlined).
"Free to read" is every OA status except closed. 2026 is a partial year: papers published so far.
"""
import csv
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
KEY = os.environ.get("OPENALEX_API_KEY")
YEARS = list(range(2010, 2027))
BASE = "type:article|review,publication_year:2010-2026"
MIN_UNI = 1000       # papers in 2010-2025 for a university to get a line
MIN_COUNTRY = 5000   # papers in 2010-2025 for a country to get a line

U15 = {"I185261750", "I141945490", "I5023651", "I154425047", "I168635309", "I70931966", "I98251732", "I125749732",
       "I153718931", "I151746483", "I43406934", "I204722609", "I46247651", "I129902397", "I32625721"}
UQ = "I49663120"  # Université du Québec, the network; its member universities are drawn, not the network itself
UNIVERSITY_NAME = re.compile(r"Universit|Polytechnique|École de Technologie|Institut National de la Recherche|HEC Montréal|"
                             r"Royal Military College|NOSM|École Nationale d'Administration|TÉLUQ", re.I)
PROVINCES = ["Alberta", "British Columbia", "Manitoba", "New Brunswick", "Newfoundland and Labrador", "Nova Scotia",
             "Ontario", "Prince Edward Island", "Quebec", "Saskatchewan", "Northwest Territories", "Nunavut", "Yukon"]


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


def series(f):
    """Papers and free-to-read papers per year for one filter."""
    out = {y: {"n": 0, "open": 0} for y in YEARS}
    for g in get("works", filter=f"{BASE},{f}" if f else BASE, group_by="publication_year,oa_status")["group_by"]:
        y = int(g["key"])
        if y in out:
            out[y]["n"] = g["count"]
            out[y]["open"] = g["count"] - sum(s["count"] for s in g["groups"] if s["key"] == "closed")
    return [{"y": y, **out[y]} for y in YEARS]


def universities():
    r = get("institutions", filter="country_code:CA,type:education", per_page=200, sort="works_count:desc",
            select="id,display_name,lineage,geo,works_count")
    picked = []
    for i in r["results"]:
        iid = i["id"].rsplit("/", 1)[-1]
        lineage = [x.rsplit("/", 1)[-1] for x in i["lineage"]]
        top = lineage == [iid] or sorted(lineage) == sorted([iid, UQ])
        if iid != UQ and top and UNIVERSITY_NAME.search(i["display_name"]) and i["works_count"] >= 1000:
            picked.append({"id": iid, "name": i["display_name"], "province": i["geo"]["region"], "u15": iid in U15})
    out = []
    for u in picked:
        s = series(f"authorships.institutions.lineage:{u['id']}")
        if sum(d["n"] for d in s if d["y"] <= 2025) >= MIN_UNI:
            out.append({**u, "s": s})
    return out


def countries():
    def grouped(extra):
        # The API returns the 200 largest groups and no more pages; the 200th country is far below MIN_COUNTRY.
        r = get("works", filter=BASE + extra, group_by="institutions.country_code,publication_year", per_page=200)
        return {g["key"].rsplit("/", 1)[-1]: (g["key_display_name"], {int(s["key"]): s["count"] for s in g["groups"]})
                for g in r["group_by"]}
    alls, opens = grouped(""), grouped(",is_oa:true")
    out = []
    for code, (name, by_year) in alls.items():
        if sum(v for y, v in by_year.items() if y <= 2025) < MIN_COUNTRY:
            continue
        ob = opens.get(code, (name, {}))[1]
        out.append({"code": code, "name": name, "s": [{"y": y, "n": by_year.get(y, 0), "open": ob.get(y, 0)} for y in YEARS]})
    return sorted(out, key=lambda c: c["name"])


def write_csv(name, rows):
    with open(RESULTS / name, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def render(data):
    template = (ROOT / "scripts" / "trends_template.html").read_text()
    (ROOT / "trends.html").write_text(template.replace("__DATA__", json.dumps(data, separators=(",", ":")).replace("</", "<\\/")))


def main():
    if "--from-json" in sys.argv:
        render(json.loads((RESULTS / "trends_data.json").read_text()))
        return
    unis = universities()
    provinces = {p: series(f'institutions.country_code:CA,authorships.institutions.geo.region:"{p}"') for p in PROVINCES}  # quoted: names have spaces
    provinces = {p: s for p, s in provinces.items() if sum(d["n"] for d in s) > 0}
    canada = series("institutions.country_code:CA")
    world = series("institutions.country_code:!null")  # every paper with at least one affiliation country
    ctry = countries()

    write_csv("oa_by_university.csv", [{"university": u["name"], "openalex_id": u["id"], "province": u["province"], "u15": u["u15"],
                                       "year": d["y"], "papers": d["n"], "free_to_read": d["open"]} for u in unis for d in u["s"]])
    write_csv("oa_by_province.csv", [{"province": p, "year": d["y"], "papers": d["n"], "free_to_read": d["open"]}
                                     for p, s in list(provinces.items()) + [("Canada", canada)] for d in s])
    write_csv("oa_by_country.csv", [{"country": c["name"], "code": c["code"], "year": d["y"], "papers": d["n"], "free_to_read": d["open"]}
                                    for c in ctry + [{"name": "World", "code": "", "s": world}] for d in c["s"]])

    data = {"asof": date.today().isoformat(), "universities": unis, "provinces": provinces, "canada": canada,
            "countries": ctry, "world": world}
    (RESULTS / "trends_data.json").write_text(json.dumps(data, separators=(",", ":")))
    render(data)
    share = lambda s, y: round(100 * s[y - 2010]["open"] / s[y - 2010]["n"], 1)
    print(f"done: {len(unis)} universities, {len(provinces)} provinces, {len(ctry)} countries; "
          f"Canada 2025 {share(canada, 2025)}%, world 2025 {share(world, 2025)}%")


if __name__ == "__main__":
    main()
