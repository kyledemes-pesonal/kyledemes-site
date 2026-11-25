"""Label each candidate: did the authors actually USE the OpenAlex database, or only mention it?

Input per work: title, type, abstract (from the API's inverted index), whether it cites the OpenAlex paper, and for
works whose title/abstract don't name OpenAlex, the passages around each mention in the open full text
(data/passages.jsonl from fetch_passages.py). The model sees batches of 40 and returns one label per work.
Roles follow oxjob #2017's literature-watch classifier so the two can be compared:
data_source, subject, tool (= used), passing, false_positive, unclear.
Model: Claude Haiku 4.5 through the Claude Code CLI (`claude -p`), with a fixed system prompt and no tools.
Output: data/labels.jsonl (resumable). Usage: python classify.py <set: titleabs|fulltext> [parallel]
Long abstracts: python classify.py late  -> relabels title/abstract works whose abstract names OpenAlex only after
the 1,800-character cut, showing the model that passage (data/labels_late_abstract.jsonl; analyse.py lets it win).
Validation: CLASSIFY_MODEL=opus python classify.py validate <sample file>  -> labels the ids in that file (drawn by
check_agreement.py --draw) into checks/labels_<model>.jsonl. Needs the Claude Code CLI (`claude`) signed in.
"""
import glob, json, os, re, subprocess, sys, threading

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
MODEL = os.environ.get('CLASSIFY_MODEL', 'haiku')
OUT = os.path.join(DATA, 'labels.jsonl')
if len(sys.argv) > 1 and sys.argv[1] == 'late':  # relabel works whose abstract names OpenAlex after the cut
    OUT = os.path.join(DATA, 'labels_late_abstract.jsonl')
if len(sys.argv) > 1 and sys.argv[1] == 'validate':
    OUT = os.path.join(DATA, '..', 'checks', f'labels_{MODEL}.jsonl')
BATCH = 40

SYSTEM = """You label scholarly works for a study of who uses OpenAlex. OpenAlex is the free, open index of scholarly works, authors, institutions, sources and topics run by the nonprofit OurResearch (openalex.org; API api.openalex.org; successor to Microsoft Academic Graph).

For each work you get its title, type, abstract and, when available, passages around the word "OpenAlex" in its full text. Decide whether the AUTHORS USED OpenAlex in their own work.

role, exactly one of:
- "data_source": the authors retrieved, searched, downloaded, queried or analysed OpenAlex data (records, metadata, citations, IDs, API, snapshot) as part of their own methods. Includes literature searches for systematic/scoping reviews that searched OpenAlex (directly or via tools like Publish or Perish), building a dataset or corpus from OpenAlex, and enriching or linking other data with OpenAlex.
- "subject": the work studies or evaluates OpenAlex itself (coverage, data quality, comparisons with Scopus, Web of Science, Dimensions, etc.).
- "tool": the work presents software, a service, a platform or a dataset that is built on or integrates OpenAlex.
- "passing": OpenAlex is mentioned but not used by the authors: background, related work, a list of possible databases, a recommendation, future work, a reference-list entry only, or a citation of the OpenAlex paper for context.
- "false_positive": the text does not refer to the OpenAlex database (e.g. a person named Alex, "open" + "Alex"), or the mention is not visible in what you were given and nothing suggests use.
- "unclear": the text you were given is too thin to decide.
Judge from the authors' own actions. A database list like "Scopus, Web of Science and OpenAlex were searched" is data_source; "databases such as Scopus or OpenAlex exist" is passing. If OpenAlex appears only in a reference list or a citation of the 2022 OpenAlex paper (W4229010617), that is passing unless the text shows use.

use (only when role is data_source, subject or tool; else null), exactly one of:
"literature_search" (finding studies for a review), "bibliometric_analysis" (counting or mapping publications, citations, collaboration, topics, trends), "dataset_building" (a corpus or dataset for machine learning, NLP or other research), "linking_enrichment" (adding IDs, affiliations, citations or metadata to other data, author or institution matching), "evaluation" (assessing OpenAlex's own coverage or quality), "software" (a tool or service), "other".

evidence: at most 15 words, quoting or closely paraphrasing the text that decided it.

Return ONLY a JSON array, one object per work, in input order: [{"id": "...", "role": "...", "use": ... , "evidence": "..."}]. No prose, no code fences."""


def abstract(inv):
    if not inv:
        return ''
    pos = [(i, w) for w, ii in inv.items() for i in ii]
    return ' '.join(w for _, w in sorted(pos))


def load():
    recs, sets = {}, {}
    for s in ('cites', 'titleabs', 'fulltext'):
        ids = set()
        for f in glob.glob(os.path.join(DATA, 'raw', s, 'page_*.json')):
            for w in json.load(open(f))['results']:
                ids.add(w['id'])
                recs[w['id']] = w
        sets[s] = ids
    pas = {}
    if os.path.exists(os.path.join(DATA, 'passages.jsonl')):
        for l in open(os.path.join(DATA, 'passages.jsonl')):
            r = json.loads(l)
            pas[r['id']] = r
    return recs, sets, pas


def item(w, sets, pas):
    ab = abstract(w.get('abstract_inverted_index'))
    d = {'id': w['id'].split('/')[-1], 'title': (w.get('title') or '')[:300], 'type': w.get('type'),
         'abstract': ab[:1800], 'cites_openalex_paper': w['id'] in sets['cites']}
    late = [m.start() for m in re.finditer(r'open ?alex', ab, re.I) if m.start() >= 1750]
    if late:  # long abstract: show the part that names OpenAlex too
        d['abstract_passages_after_cut'] = [ab[max(0, k - 500): k + 500] for k in late[:3]]
    p = pas.get(w['id'])
    if p and p.get('status') == 'ok':
        d['fulltext_mentions'] = p['n_mentions']
        d['fulltext_mentions_before_reference_list'] = p['n_body_mentions'] if p['has_refs_heading'] else 'unknown'
        d['passages'] = [x[:1000] for x in p['passages'][:4]]
    elif w['id'] not in sets['titleabs']:
        d['passages'] = 'full text not available to you'
    return d


def run_batch(items):
    prompt = 'Label these works:\n' + '\n'.join(json.dumps(i, ensure_ascii=False) for i in items)
    cmd = ['claude', '-p', '--model', MODEL, '--system-prompt', SYSTEM, '--tools', '', '--strict-mcp-config',
           '--setting-sources', '', '--no-session-persistence', '--output-format', 'text']
    for attempt in range(3):
        r = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=600, cwd='/tmp')
        txt = r.stdout
        try:
            arr = json.loads(txt[txt.index('['): txt.rindex(']') + 1])
            got = {('W' + str(a['id']).split('W')[-1]): a for a in arr if isinstance(a, dict) and a.get('id')}
            if len(got) >= len(items) * 0.9:
                return got
        except Exception:  # noqa: BLE001
            pass
        print('  retry batch', attempt, (r.stderr or txt)[:200], flush=True)
    return {}


def main():
    which = sys.argv[1]
    par = int(sys.argv[3 if which == 'validate' else 2]) if len(sys.argv) > (3 if which == 'validate' else 2) else 4
    recs, sets, pas = load()
    if which == 'titleabs':
        ids = sorted(sets['titleabs'])
    elif which == 'late':
        ids = sorted(i for i in sets['titleabs']
                     if any(m.start() >= 1750 for m in re.finditer(r'open ?alex', abstract(recs[i].get('abstract_inverted_index')), re.I))
                     and not re.search(r'open ?alex', abstract(recs[i].get('abstract_inverted_index'))[:1750] + ' ' + (recs[i].get('title') or ''), re.I))
    elif which == 'validate':
        ids = [l.strip() for l in open(sys.argv[2]) if l.strip()]
    else:  # works whose title/abstract don't name OpenAlex, once their passages are fetched
        ids = sorted(i for i in (sets['fulltext'] | sets['cites']) - sets['titleabs'] if i in pas)
    done = set()
    if os.path.exists(OUT):
        done = {json.loads(l)['work'] for l in open(OUT)}
    ids = [i for i in ids if i not in done]
    batches = [ids[k:k + BATCH] for k in range(0, len(ids), BATCH)]
    print(which, 'works', len(ids), 'batches', len(batches), flush=True)
    lock, q = threading.Lock(), list(batches)

    def worker():
        while True:
            with lock:
                if not q:
                    return
                b = q.pop(0)
            got = run_batch([item(recs[i], sets, pas) for i in b])
            with lock:
                with open(OUT, 'a') as f:
                    for i in b:
                        a = got.get(i.split('/')[-1])
                        if a:
                            f.write(json.dumps({'work': i, 'set': which, 'role': a.get('role'), 'use': a.get('use'),
                                                'evidence': a.get('evidence'), 'model': MODEL}, ensure_ascii=False) + '\n')
                print(len(batches) - len(q), 'of', len(batches), 'batches', flush=True)

    ts = [threading.Thread(target=worker) for _ in range(par)]
    [t.start() for t in ts]
    [t.join() for t in ts]


if __name__ == '__main__':
    main()
