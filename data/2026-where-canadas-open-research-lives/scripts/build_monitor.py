"""Build the data behind the Canadian Open Access Monitor from the OpenAlex API.

Standard library only. Set OPENALEX_API_KEY in the environment if you have one (recommended; the
script makes about 150 requests). Run from this folder:

    python3 scripts/build_monitor.py

Writes results/*.csv (the numbers behind every chart), results/monitor_data.json, and monitor.html
(the dashboard, built from scripts/monitor_template.html with the data inlined).
"""
import csv
import json
import os
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
KEY = os.environ.get("OPENALEX_API_KEY")
YEARS = range(2010, 2026)

# Tri-agency = OpenAlex funder records for NSERC, SSHRC, CIHR and their sub-units, plus Canada Research
# Chairs, CERC and CFREF (and CIHR's predecessor MRC).
AGENCIES = {
    "cihr": "F4320334506|F4320321563|F3340254956|F8543264415|F4320324195",
    "nserc": "F4320334593|F4320321487",
    "sshrc": "F4320334617|F7697234222",
}
TRI = "|".join(AGENCIES.values()) + "|F4320320994|F4320321481|F4320326644"
ROUTES = ["gold", "diamond", "hybrid", "green", "bronze", "closed"]
BASE = "type:article|review"

# The agencies' 2025 KPI baselines (Tri-Agency statement, 5 Oct 2026).
AGENCY_KPI = {"Canadian-authored": 68.6, "NSERC-funded": 73.0, "SSHRC-funded": 72.4, "CIHR-funded": 85.3}

# Peer funders for comparison (OpenAlex funder IDs).
PEERS = {
    "Wellcome (UK)": "F4320311904", "NWO (Netherlands)": "F4320321800", "ERC (EU)": "F4320338335",
    "UKRI (UK)": "F4320314731|F4320334626|F4320334627", "SNSF (Switzerland)": "F4320320924",
    "European Commission": "F4320320300", "FWF (Austria)": "F4320321181", "Swedish Research Council": "F4320322581",
    "HHMI (US)": "F4320306082", "NIH (US)": "F4320332161", "Gates Foundation": "F4320306137", "DFG (Germany)": "F4320320879",
    "Research Council of Norway": "F4320323299", "ANR (France)": "F4320320883", "NHMRC (Australia)": "F4320334705",
    "NSF (US)": "F4320306076", "ARC (Australia)": "F4320334704", "JSPS (Japan)": "F4320334764", "FAPESP (Brazil)": "F4320320997",
    "NSFC (China)": "F4320321001",
}

# Publishers' zero-embargo accepted-manuscript policies, read from their public pages on 18 Nov 2026.
PUBLISHERS = {
    "P4310320990": ("Elsevier", "no", "https://www.elsevier.com/about/policies-and-standards/sharing"),
    "P4310319965": ("Springer Nature", "no", "https://www.springernature.com/gp/open-science/policies/journal-policies"),
    "P4310320006": ("ACS", "fee", "https://acsopenscience.org/researchers/oa-pricing/"),
    "P4310320547": ("Taylor & Francis", "no", "https://authorservices.taylorandfrancis.com/publishing-open-access/zero-embargo-green-open-access/"),
    "P4310319808": ("IEEE", "fee", "https://open.ieee.org/repository-license-fee/"),
    "P4310320595": ("Wiley", "no", "https://authors.wiley.com/author-resources/Journal-Authors/licensing/self-archiving.html"),
    "P4310312929": ("Canadian Science Publishing", "yes", "https://blog.cdnsciencepub.com/supporting-green-open-access-sustainably/"),
    "P4310320017": ("Sage", "yes", "https://www.sagepub.com/journals/information-for-authors/publishing-options/green-open-access"),
    "P4310311648": ("Oxford University Press", "unknown", None),
    "P4310320261": ("APS", "unknown", None),
}

# Canadian repository-type sources that are not article repositories (data, talks, archives).
NOT_ARTICLE_REPOS = {"S7407050857", "S4306402326", "S7407051724", "S7407051176", "S7407050688", "S7407052203",
                     "S4306400638", "S7407053128", "S7407053124", "S7407053126"}


def get(path, **params):
    if KEY:
        params["api_key"] = KEY
    url = "https://api.openalex.org/" + path + "?" + urllib.parse.urlencode(params, safe=":,|!<>")
    for attempt in range(6):
        try:
            with urllib.request.urlopen(url, timeout=90) as r:
                return json.load(r)
        except Exception as e:  # rate limits and timeouts: back off and retry
            err = e
            time.sleep(2 * (attempt + 1))
    raise err


def count(filter_):
    return get("works", filter=filter_, per_page=1)["meta"]["count"]


def by_year(filter_):
    r = get("works", filter=filter_, group_by="publication_year")
    return {int(g["key"]): g["count"] for g in r["group_by"]}


def by_year_route(filter_):
    r = get("works", filter=filter_, group_by="publication_year,oa_status")
    out = {}
    for g in r["group_by"]:
        out[int(g["key"])] = {s["key"]: s["count"] for s in g["groups"]}
        out[int(g["key"])]["n"] = g["count"]
    return out


def canadian_repositories():
    """The 100 largest repository sources hosted by Canadian institutions."""
    insts, cursor = [], "*"
    while cursor:
        r = get("institutions", filter="country_code:CA,works_count:>500", per_page=200, cursor=cursor, select="id")
        if not r["results"]:
            break
        insts += [x["id"].rsplit("/", 1)[-1] for x in r["results"]]
        cursor = r["meta"].get("next_cursor")
    repos = {}
    for i in range(0, len(insts), 50):
        r = get("sources", filter="type:repository,host_organization:" + "|".join(insts[i:i + 50]), per_page=200,
                select="id,display_name,works_count")
        for s in r["results"]:
            repos[s["id"].rsplit("/", 1)[-1]] = s
    r = get("sources", filter="type:repository,country_code:CA", per_page=200, select="id,display_name,works_count")
    for s in r["results"]:
        repos[s["id"].rsplit("/", 1)[-1]] = s
    keep = sorted((s for k, s in repos.items() if k not in NOT_ARTICLE_REPOS), key=lambda s: -s["works_count"])[:100]
    return [s["id"].rsplit("/", 1)[-1] for s in keep], keep


def write_csv(name, rows, fields):
    with open(RESULTS / name, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def main():
    RESULTS.mkdir(exist_ok=True)
    yrs = f"publication_year:{YEARS[0]}-{YEARS[-1]}"
    repo_ids, repo_rows = canadian_repositories()
    carepo = "locations.source.id:" + "|".join(repo_ids)
    write_csv("canadian_repositories.csv", [{"id": s["id"], "name": s["display_name"], "works": s["works_count"]} for s in repo_rows],
              ["id", "name", "works"])

    sets = {"canada": "institutions.country_code:CA", "tri": f"funders.id:{TRI}",
            **{k: f"funders.id:{v}" for k, v in AGENCIES.items()}}
    series, rows = {}, []
    for name, f in sets.items():
        routes = by_year_route(f"{BASE},{yrs},{f}")
        rep = by_year(f"{BASE},{yrs},{f},{carepo}")
        pmc = by_year(f"{BASE},{yrs},{f},locations.source.id:S2764455111|S4306400806")
        series[name] = []
        for y in YEARS:
            d = routes.get(y, {"n": 0})
            row = {"y": y, "n": d["n"], **{r: d.get(r, 0) for r in ROUTES}, "carepo": rep.get(y, 0), "pmc": pmc.get(y, 0)}
            series[name].append(row)
            rows.append({"set": name, **row})
    write_csv("routes_by_year.csv", rows, ["set", "y", "n"] + ROUTES + ["carepo", "pmc"])

    award_years = range(2015, YEARS[-1] + 1)
    award_by_agency = {}
    rows = []
    for name, f in AGENCIES.items():
        tot = by_year(f"{BASE},publication_year:2015-{YEARS[-1]},funders.id:{f}")
        aw = by_year(f"{BASE},publication_year:2015-{YEARS[-1]},funders.id:{f},awards.funder_id:{f}")
        award_by_agency[name.upper()] = [{"y": y, "n": tot.get(y, 0), "award": aw.get(y, 0)} for y in award_years]
        rows += [{"agency": name.upper(), **r} for r in award_by_agency[name.upper()]]
    tot = by_year(f"{BASE},publication_year:2015-{YEARS[-1]},funders.id:{TRI}")
    aw = by_year(f"{BASE},publication_year:2015-{YEARS[-1]},funders.id:{TRI},awards.funder_id:{TRI}")
    award = [{"y": y, "n": tot.get(y, 0), "award": aw.get(y, 0)} for y in award_years]
    rows += [{"agency": "TRI", **r} for r in award]
    write_csv("grant_numbers_by_year.csv", rows, ["agency", "y", "n", "award"])

    last = YEARS[-1]
    f_last = f"{BASE},publication_year:{last},funders.id:{TRI}"
    r = get("works", filter=f_last, group_by="primary_location.source.publisher_lineage,oa_status", per_page=200)
    pubs = []
    for g in r["group_by"]:
        pid = g["key"].rsplit("/", 1)[-1]
        if pid in PUBLISHERS:
            nm, route, link = PUBLISHERS[pid]
            d = {s["key"]: s["count"] for s in g.get("groups", [])}
            pubs.append({"pub": nm, "n": g["count"], "closed": d.get("closed", 0), "route": route, "link": link})
    pubs.sort(key=lambda x: -x["closed"])
    write_csv("closed_by_publisher.csv", pubs, ["pub", "n", "closed", "route", "link"])

    def by_field(f):
        return {g["key_display_name"]: g["count"] for g in get("works", filter=f, group_by="primary_topic.field.id")["group_by"]}
    fa, fo, fc = by_field(f_last), by_field(f_last + ",is_oa:true"), by_field(f_last + ",oa_status:closed")
    fields = sorted(({"field": k, "n": v, "oa": fo.get(k, 0), "closed": fc.get(k, 0)} for k, v in fa.items() if v >= 200), key=lambda x: -x["n"])
    write_csv("open_by_field.csv", fields, ["field", "n", "oa", "closed"])

    peers = [{"funder": "Tri-agency (Canada)", "tri": True, "f": TRI}] + [{"funder": k, "tri": False, "f": v} for k, v in PEERS.items()]
    for p in peers:
        n, c = count(f"{BASE},publication_year:{last},funders.id:{p['f']}"), count(f"{BASE},publication_year:{last},funders.id:{p['f']},is_oa:false")
        p["oa"] = round(100 * (n - c) / n, 1)
        p.pop("f")
    peers.sort(key=lambda x: -x["oa"])
    write_csv("funders.csv", peers, ["funder", "tri", "oa"])

    lic = {g["key"].rsplit("/", 1)[-1]: g["count"] for g in get("works", filter=f_last, group_by="best_oa_location.license")["group_by"]}

    usd, n_with, cursor = 0.0, 0, "*"
    while cursor:
        r = get("works", filter=f_last + ",oa_status:gold|hybrid", per_page=200, cursor=cursor, select="id,apc_list")
        if not r["results"]:
            break
        for w in r["results"]:
            v = (w.get("apc_list") or {}).get("value_usd")
            if v:
                usd += v
                n_with += 1
        cursor = r["meta"].get("next_cursor")

    def oa_share(rows_):
        x = rows_[-1]
        return round(100 * (x["n"] - x["closed"]) / x["n"], 1)
    kpi = [{"label": "Canadian-authored", "ours": oa_share(series["canada"]), "agency": AGENCY_KPI["Canadian-authored"]},
           {"label": "NSERC-funded", "ours": oa_share(series["nserc"]), "agency": AGENCY_KPI["NSERC-funded"]},
           {"label": "SSHRC-funded", "ours": oa_share(series["sshrc"]), "agency": AGENCY_KPI["SSHRC-funded"]},
           {"label": "CIHR-funded", "ours": oa_share(series["cihr"]), "agency": AGENCY_KPI["CIHR-funded"]}]
    write_csv("kpi_comparison.csv", kpi, ["label", "ours", "agency"])

    data = {"asof": date.today().isoformat(), "series": series, "award": award, "award_by_agency": award_by_agency,
            "pubs": [{k: v for k, v in p.items() if k != "link"} for p in pubs],
            "pub_links": {p["pub"]: p["link"] for p in pubs if p["link"]}, "fields": fields, "funders": peers,
            "license": lic, "apc": {"usd": usd, "n_with": n_with}, "kpi": kpi}
    (RESULTS / "monitor_data.json").write_text(json.dumps(data, separators=(",", ":")))
    template = (ROOT / "scripts" / "monitor_template.html").read_text()
    (ROOT / "monitor.html").write_text(template.replace("__DATA__", json.dumps(data, separators=(",", ":")).replace("</", "<\\/")))
    t = series["tri"][-1]
    print(f"done: {data['asof']}; tri-agency {last}: {t['n']} papers, {oa_share(series['tri'])}% free to read, "
          f"{round(100 * t['carepo'] / t['n'], 1)}% with a Canadian repository copy; APC list value US${usd / 1e6:.1f}M")


if __name__ == "__main__":
    main()
