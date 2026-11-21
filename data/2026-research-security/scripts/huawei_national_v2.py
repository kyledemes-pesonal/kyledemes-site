"""Huawei support in acknowledgements, all of Canada. v2 (20 Nov 2026) of huawei_national.py, after the pre-publication check.
Changes from v1:
- the exclusion regex matches the word "intern(s/ship)" only, so "International" no longer drops a mention (v1 lost 7);
- the support test ignores the matched name itself, so "Noah's Ark Lab" no longer passes on its own "lab";
- each supporting work is credited to every Canadian institution in its authorships' lineage (v1 used direct IDs only,
  though its docstring said lineage), so a university gets its institutes' and hospitals-in-lineage papers.
Candidates: Canadian works (all types) 2016-2025 whose OpenAlex full text mentions Huawei (fulltext.search:huawei);
GROBID acknowledgement/funding text from content.openalex.org via fetch_acks.py. Re-uses the saved candidate and
acknowledgement files unless run with --refresh. Output ../results/huawei_national_v2_summary.json (counts only).
The candidate and acknowledgement files (huawei_nat_works.json, huawei_nat_acks.jsonl) hold author names and
acknowledgement text: they stay local and are not published."""
import json, re, sys, collections, subprocess, os
import oa

S = lambda u: u.rsplit('/', 1)[-1]
WORKS, ACKS = '../results/huawei_nat_works.json', '../results/huawei_nat_acks.jsonl'
P = re.compile(r'huawei|hisilicon|futurewei|noah.?s ark lab', re.I)
SUPPORT = re.compile(r'support|fund|grant|gift|lab|sponsor|partner|donat|collaborat|award|chair|program|centre|center|innovation', re.I)
X = re.compile(r'consult|employee|\bintern(s|ship|ships)?\b|mindspore|pku|industrial partners|generous support of our industrial|donations|e-mail', re.I)
PRODUCT = re.compile(r'\s*(mate|p\d|nova|kirin|ascend|atlas)', re.I)


def candidates(refresh):
    if not refresh and os.path.exists(WORKS):
        return json.load(open(WORKS))
    ws, cur = [], '*'
    while cur:
        r = oa.get('/works', filter='fulltext.search:huawei,institutions.country_code:CA,publication_year:2016-2025', per_page=200,
                   cursor=cur, select='id,title,publication_year,type,has_content,authorships,funders')
        ws += r['results']; cur = r['meta'].get('next_cursor') if r['results'] else None
    json.dump(ws, open(WORKS, 'w'))
    subprocess.run([sys.executable, 'fetch_acks.py', WORKS, ACKS], check=True)
    return ws


def supported(t):
    for m in P.finditer(t):
        win = t[max(0, m.start() - 150):m.end() + 150]
        rest = t[max(0, m.start() - 150):m.start()] + ' ' + t[m.end():m.end() + 150]
        if SUPPORT.search(rest) and not X.search(win) and not PRODUCT.match(t[m.end():m.end() + 8]):
            return win
    return None


def main():
    ws = candidates('--refresh' in sys.argv)
    acks = {json.loads(l)['w']: json.loads(l) for l in open(ACKS)}
    meta = {S(w['id']): w for w in ws}
    hits = {wid: win for wid, r in acks.items() if wid in meta and (win := supported(r.get('ack') or ''))}
    inst = collections.defaultdict(collections.Counter); inst_name = {}
    for wid in hits:
        w = meta[wid]; y = w['publication_year']
        ids = set()
        for a in w['authorships']:
            for ins in a.get('institutions') or []:
                inst_name[S(ins['id'])] = ins['display_name']
                if ins.get('country_code') == 'CA':
                    ids |= {S(x) for x in (ins.get('lineage') or [ins['id']])}
        for i in ids:
            inst[i][y] += 1
    by_year = collections.Counter(meta[w]['publication_year'] for w in hits)
    fid = sum(1 for w in hits if any(re.search(r'huawei|futurewei', f.get('display_name') or '', re.I) for f in meta[w].get('funders') or []))
    top = sorted(inst, key=lambda i: -sum(inst[i].values()))[:25]
    out = {'candidates': len(ws), 'with_ack_text': len(acks), 'supported': len(hits), 'funder_field_lists_huawei_or_futurewei': fid,
           'by_year': dict(sorted(by_year.items())),
           'by_type': dict(collections.Counter(meta[w].get('type') for w in hits)),
           'institutions': {i: {'name': inst_name.get(i), 'by_year': dict(inst[i])} for i in top}}
    json.dump(out, open('../results/huawei_national_v2_summary.json', 'w'), ensure_ascii=False, indent=1)
    print('candidates', len(ws), 'acks', len(acks), 'supported', len(hits), 'funder field lists Huawei/Futurewei', fid)
    print('by year', sorted(by_year.items()))
    for i in top:
        d = inst[i]; s = lambda ys: sum(d.get(y, 0) for y in ys)
        print(f"{(inst_name.get(i) or i)[:34]:34} 19-21 {s(range(2019, 2022)):3d}  20-21 {s([2020, 2021]):3d}  22-23 {s([2022, 2023]):3d}  24-25 {s([2024, 2025]):3d}")


if __name__ == '__main__':
    main()
