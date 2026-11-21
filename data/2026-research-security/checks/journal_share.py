"""Check 4: how many 'journal articles' (type:article) are not in journals (primary_location.source.type), overall and in
sensitive subfields; and whether restricting to journal sources moves the CA-CN share, the sensitive-field China share,
and the funded/other shares."""
import concurrent.futures as cf
import oax
SENS = '1702|1705|1707|1708|1709|1711|1712|1710|1703|2202|2207|2208|2209|2210|2212|2203|2102|2103|2104|2105|2501|2502|2503|2504|2505|2506|2507|2508|3104|3105|3107|3108|1305|2204|2402'
NONSENS = '27|29|35|36|33|12|32|20|14|23|11|19|28|30|34|18'
FUND = 'F4320334593|F4320334506|F4320334617|F7697234222|F4320319952|F4320320995'
CLS = {'all': '', 'sens': f',primary_topic.subfield.id:{SENS}', 'nonsens': f',primary_topic.field.id:{NONSENS}'}
YEARS = [2020, 2025]
out = {}
def grp(args):
    c, y, cn = args
    f = f'type:article,institutions.country_code:CA,publication_year:{y}' + CLS[c] + (',institutions.country_code:CN' if cn else '')
    return c, y, cn, oax.group(f, 'primary_location.source.type')
with cf.ThreadPoolExecutor(4) as ex:
    for c, y, cn, g in ex.map(grp, [(c, y, cn) for c in CLS for y in YEARS for cn in (False, True)]):
        out.setdefault(c, {}).setdefault(str(y), {})['CN' if cn else 'CA'] = g
print('primary_location.source.type breakdown (CA type:article)')
for c in CLS:
    for y in YEARS:
        g = out[c][str(y)]['CA']; tot = sum(g.values()); j = g.get('journal', 0)
        gc = out[c][str(y)]['CN']; totc = sum(gc.values()); jc = gc.get('journal', 0)
        print(f"{c:8} {y}: total {tot:6d}  " + ', '.join(f'{k} {v} ({100*v/tot:.1f}%)' for k, v in sorted(g.items(), key=lambda kv: -kv[1])))
        print(f"{'':8} {y}: CN share all {100*totc/tot:.2f}%  journal-only {100*jc/j:.2f}%  | non-journal CN share {100*(totc-jc)/max(1,tot-j):.2f}%")
# funded vs other, journal-only
fo = {}
def fj(args):
    y, cn, src = args
    f = f'type:article,institutions.country_code:CA,publication_year:{y},funders.id:{FUND}' + (',institutions.country_code:CN' if cn else '') + (',primary_location.source.type:journal' if src else '')
    return y, cn, src, oax.count(f)
def tj(args):
    y, cn = args
    f = f'type:article,institutions.country_code:CA,publication_year:{y},primary_location.source.type:journal' + (',institutions.country_code:CN' if cn else '')
    return y, cn, oax.count(f)
with cf.ThreadPoolExecutor(4) as ex:
    for y, cn, src, n in ex.map(fj, [(y, cn, s) for y in YEARS for cn in (False, True) for s in (False, True)]):
        fo.setdefault(str(y), {})[('CN' if cn else 'CA') + ('_journal' if src else '')] = n
    jt = {}
    for y, cn, n in ex.map(tj, [(y, cn) for y in YEARS for cn in (False, True)]):
        jt.setdefault(str(y), {})['CN' if cn else 'CA'] = n
for y in map(str, YEARS):
    f = fo[y]; t = jt[y]
    print(f"{y} funded share all-sources {100*f['CN']/f['CA']:.2f}%  journal-only {100*f['CN_journal']/f['CA_journal']:.2f}% | "
          f"other share journal-only {100*(t['CN']-f['CN_journal'])/(t['CA']-f['CA_journal']):.2f}%  (journal CA {t['CA']}, CN {t['CN']})")
oax.dump({'by_source_type': out, 'funded': fo, 'journal_totals': jt}, 'journal_share.json')
