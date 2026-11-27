"""v3: share of opened papers (v3 pure set) with an arXiv copy posted before the opening year.
Written for the published folder (27 Nov 2026); it repeats a count made during the analysis for the v3 pure set.
Inputs: data/v2_q10_panel.csv (Q10: source x publication year x earliest arXiv posting year 'axy', 0 = none) and
results/v3/stacks_v3.tsv (v3 matching). Q10 is not cleaned for duplicate records, so its paper count (352,540) is a little
above the cleaned v3 panel's 346,011. Output: results/v3/arxiv_share.json.
Run from the folder above scripts/: python -I scripts/v3_arxiv_share.py [root] [output file]"""
import json, os, sys
import pandas as pd
ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, 'results', 'v3', 'arxiv_share.json')
q = pd.read_csv(os.path.join(ROOT, 'data', 'v2_q10_panel.csv'), usecols=['src', 'py', 'axy', 'n_articles'])
sz = q.drop_duplicates(['src', 'py', 'axy'])          # n_articles repeats on every citing-year row of a unit
st = pd.read_csv(os.path.join(ROOT, 'results', 'v3', 'stacks_v3.tsv'), sep='\t')
pure = st[st.group == 'pure']
papers = arxiv_before_T = 0
by_program = {}
for r in pure.itertuples():
    s = sz[(sz.src == r.treated) & (sz.py >= r.lo) & (sz.py <= r.hi)]
    n, a = int(s.n_articles.sum()), int(s[(s.axy > 0) & (s.axy < r.T)].n_articles.sum())
    papers += n; arxiv_before_T += a
    b = by_program.setdefault(r.program, {'papers': 0, 'arxiv_before_T': 0}); b['papers'] += n; b['arxiv_before_T'] += a
out = {'openings': int(len(pure)), 'papers_q10': papers, 'arxiv_before_T': arxiv_before_T,
       'share_arxiv_before_T': arxiv_before_T / papers, 'by_program': by_program,
       'rule': 'arXiv posting year (from the arXiv id) earlier than the opening year T; copies posted in or after T count as none'}
json.dump(out, open(OUT, 'w'), indent=1)
print(out['openings'], papers, arxiv_before_T, round(100 * out['share_arxiv_before_T'], 2))
