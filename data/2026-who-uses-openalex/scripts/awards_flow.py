"""Right side of the 'who pays' flow chart: distinct grants (award records) listed on the 4,672 papers that used
OpenAlex, grouped by funder. 'both' = funders that also pay OpenAlex (grant-maker or paying member, per
openalex.org/institutional-supporters and OpenAlex's grant announcements). Output: results/awards_by_group.json"""
import csv, collections, glob, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, '..')
recs = {}
for f in glob.glob(os.path.join(D, 'data', 'raw', '*', 'page_*.json')):
    for w in json.load(open(f))['results']:
        recs[w['id']] = w
rows = list(csv.DictReader(open(os.path.join(D, 'results', 'corpus.csv'))))
works = [recs['https://openalex.org/' + r['work_id']] for r in rows]

BOTH = re.compile(r'wellcome|funda..o para a ci|vetenskapsr|swedish research council|nederlandse organisatie|'
                  r'dutch research council|\bNWO\b|japan science and technology|agencia nacional de investigaci|\bANID\b|'
                  r'austrian science fund|^fonds zur f|howard hughes|arcadia|navigation fund|schmidt sciences|'
                  r'enseignement sup.rieur|higher education, research', re.I)
EU = re.compile(r'european commission|horizon (europe|2020)|h2020|european research council|nextgenerationeu|'
                r'seventh framework|european regional development|erasmus|marie (sk|curie)|european union', re.I)
GROUPS = [
    ('both', 'Funders that also pay for OpenAlex', lambda n: bool(BOTH.search(n))),
    ('eu', 'EU programmes', lambda n: bool(EU.search(n))),
    ('nsf', 'US National Science Foundation', lambda n: n == 'National Science Foundation'),
    ('nsfc', 'China’s NSFC', lambda n: 'National Natural Science Foundation of China' in n),
    ('de', 'Germany’s DFG and research ministry', lambda n: bool(re.search(r'Deutsche Forschungsgemeinschaft|Bundesministerium f', n))),
    ('es', 'Spain’s research agency and ministry', lambda n: bool(re.search(r'Agencia Estatal de Investigaci|Ministerio de (Ciencia|Econom|Universidades)', n))),
    ('br', 'Brazil’s FAPESP, CAPES and CNPq', lambda n: bool(re.search(r'Funda..o de Amparo . Pesquisa do Estado de S|Coordena..o de Aperfei|Conselho Nacional de Desenvolvimento Cient', n))),
    ('nih', 'US National Institutes of Health', lambda n: n == 'National Institutes of Health' or bool(re.search(r'^National (Cancer Institute|Institute (of|on) .*(Health|Disease|Aging|Abuse|Alcohol|Disorders|Imaging|Sciences))|^National Heart, Lung', n))),
]
awards = {}
for w in works:
    for a in w.get('awards') or []:
        awards[a['id']] = a.get('funder_display_name') or ''
count, funders = collections.Counter(), collections.defaultdict(set)
for name in awards.values():
    g = next((k for k, _, f in GROUPS if f(name)), 'other')
    count[g] += 1
    funders[g].add(name)
out = {'distinct_awards': len(awards), 'papers_with_awards': sum(bool(w.get('awards')) for w in works),
       'groups': [{'slug': k, 'label': lab, 'grants': count[k], 'funders': len(funders[k])} for k, lab, _ in GROUPS]
       + [{'slug': 'other', 'label': 'other', 'grants': count['other'], 'funders': len(funders['other'])}],
       'both_detail': collections.Counter(n for n in awards.values() if BOTH.search(n)).most_common()}
json.dump(out, open(os.path.join(D, 'results', 'awards_by_group.json'), 'w'), indent=1, ensure_ascii=False)
print(json.dumps(out, indent=1, ensure_ascii=False))
