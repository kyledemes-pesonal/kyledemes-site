"""How often a second model (Claude Opus) agrees with the labels the analysis uses.
  python check_agreement.py --draw   draws the two random samples of 100 (title/abstract works; works read in the body)
                                     into checks/sample_titleabs.txt and checks/sample_body.txt
  CLASSIFY_MODEL=opus python classify.py validate ../checks/sample_titleabs.txt   (and the body file)
  python check_agreement.py          compares checks/labels_opus.jsonl with the final labels -> results/agreement.json
On 24 Nov 2026 the body sample was drawn while labelling was still running (from the first 2,644 body-read works), so a
fresh --draw gives a different sample. checks/ holds per-paper labels and is not published.
"""
import collections, json, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA, CHK, RES = (os.path.join(HERE, '..', d) for d in ('data', 'checks', 'results'))
USED = {'data_source', 'subject', 'tool'}
labels = {}
for fn in ('labels.jsonl', 'labels_late_abstract.jsonl'):
    for l in open(os.path.join(DATA, fn)):
        r = json.loads(l)
        labels[r['work']] = r
if '--draw' in sys.argv:
    pas = {json.loads(l)['id']: json.loads(l) for l in open(os.path.join(DATA, 'passages.jsonl'))}
    ta = sorted(w for w, l in labels.items() if l['set'] == 'titleabs')
    body = sorted(w for w, l in labels.items() if l['set'] == 'fulltext' and pas.get(w, {}).get('status') == 'ok')
    os.makedirs(CHK, exist_ok=True)
    random.seed(20261124)
    open(os.path.join(CHK, 'sample_titleabs.txt'), 'w').write('\n'.join(random.sample(ta, 100)) + '\n')
    random.seed(20261125)
    open(os.path.join(CHK, 'sample_body.txt'), 'w').write('\n'.join(random.sample(body, 100)) + '\n')
    sys.exit('samples drawn')
opus = {json.loads(l)['work']: json.loads(l) for l in open(os.path.join(CHK, 'labels_opus.jsonl'))}
out = {}
for name in ('titleabs', 'body'):
    ids = [l.strip() for l in open(os.path.join(CHK, f'sample_{name}.txt')) if l.strip()]
    both = [i for i in ids if i in opus and i in labels]
    agree = sum((labels[i]['role'] in USED) == (opus[i]['role'] in USED) for i in both)
    uu = [i for i in both if labels[i]['role'] in USED and opus[i]['role'] in USED]
    out[name] = {'compared': len(both), 'agree_used_or_not': agree,
                 'both_used': len(uu), 'same_use_category': sum(labels[i].get('use') == opus[i].get('use') for i in uu)}
out['total'] = {k: sum(out[n][k] for n in ('titleabs', 'body')) for k in out['titleabs']}
json.dump(out, open(os.path.join(RES, 'agreement.json'), 'w'), indent=1)
print(json.dumps(out, indent=1))
