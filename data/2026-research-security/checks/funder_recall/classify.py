"""Step 3: parse each cached TEI, extract acknowledgement + funding text, decide ack_tri (text credits NSERC, CIHR, SSHRC
or CFI), compare with field_tri (OpenAlex funders lists one of the 6 IDs; local download of 18 Nov, live value alongside).
usage: classify.py <cache_dir> -> works.csv (one row per downloaded work, all decisions + snippets), acks.jsonl (texts)

Text used for ack_tri ("ack text"):
  - <div type="acknowledgement"> and <div type="funding"> (GROBID back matter)
  - <funder> org names in the TEI header
  - body / annex divs whose heading is Acknowledg*/Funding/Financial support/Remerciements/Financement
  - footnotes (<note place="foot">) that talk about support, funding or grants
Never: references, the conflict-of-interest div, author affiliations.
Broad sensitivity (any_tri_ctx): a tri-agency name anywhere in body/back text (no references, no conflict div), inside a sentence
that also has a support word. Catches acknowledgements GROBID misfiled into the body."""
import csv, gzip, json, os, re, sys, glob
import xml.etree.ElementTree as ET
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = sys.argv[1]
NS = '{http://www.tei-c.org/ns/1.0}'
FUND = {'F4320334593': 'NSERC', 'F4320334506': 'CIHR', 'F4320334617': 'SSHRC', 'F7697234222': 'SSHRC', 'F4320319952': 'CFI', 'F4320320995': 'CFI'}
I = re.I
PAT = {
    'NSERC': [re.compile(r'\bNSERC\b|\bCRSNG\b'), re.compile(r'(?:Natural|National)\s+Sciences?\s+(?:and|&)\s+Engineering\s+(?:Research\s+)?Council|Conseil\s+de\s+recherches?\s+en\s+sciences\s+naturelles\s+et\s+(?:en\s+)?g[ée]nie', I)],
    'CIHR': [re.compile(r'\bCIHR\b|\bIRSC\b'), re.compile(r'Canadian\s+Institutes?\s+(?:of|for)\s+Health\s+Research|Instituts?\s+de\s+recherche\s+en\s+sant[ée]\s+du\s+Canada', I)],
    'SSHRC': [re.compile(r'\bSSHRC\b|\bCRSH\b'), re.compile(r'Social\s+Sciences?\s+(?:and|&)\s+Humanities\s+Research\s+Council|Conseil\s+de\s+recherches?\s+en\s+sciences\s+humaines', I)],
    'CFI': [re.compile(r'Canad(?:a|ian)\s+Foundation\s+for\s+Innovation|Fondation\s+canadienne\s+pour\s+l.\s*innovation', I)],
}
CFI_BARE = re.compile(r'\bCFI\b(?!\s*[=<>≥≤:]|\s*(?:value|index|of\s+0))')       # bare acronym, not a fit-index statistic
FCI_BARE = re.compile(r'\bFCI\b')
CANADA_CTX = re.compile(r'Canad|Qu[ée]bec|Ontario|JELF|Evans|Leaders\s+Fund|Innovation\s+Fund|NSERC|CIHR|SSHRC|infrastructure', I)
NOT_CFI = re.compile(r'comparative\s+fit|fit\s+ind', I)
CRC = re.compile(r'Canada\s+(?:Excellence\s+)?Research\s+Chairs?|Chaires?\s+de\s+recherche\s+du\s+Canada|\bCERC\b|\bCRC\s+(?:Tier|program)', I)
OTHER = re.compile(r'Canada\s+First\s+Research\s+Excellence|CFREF|Vanier|Banting|Canada\s+Graduate\s+Scholarship|New\s+Frontiers\s+in\s+Research|\bNFRF\b|Networks?\s+of\s+Centres\s+of\s+Excellence|Mitacs|Genome\s+Canada', I)
HEAD_RE = re.compile(r'acknowledg|funding|financial\s+(?:support|disclosure)|grant\s+(?:support|information)|sources?\s+of\s+(?:support|funding)|remerciement|financement', I)
NOTE_RE = re.compile(r'support|fund|grant|financ|NSERC|CIHR|SSHRC', I)
SUPPORT = re.compile(r'support|fund|grant|financ|award|scholarship|fellowship|chair|thank|acknowledg|sponsor|program|discovery|subvention', I)
def tx(el): return re.sub(r'\s+', ' ', ' '.join(el.itertext())).strip()
def tri_hits(t):
    """Return {agency: first matching snippet} for the text."""
    out = {}
    for ag, pats in PAT.items():
        for p in pats:
            m = p.search(t)
            if m: out[ag] = t[max(0, m.start() - 80):m.end() + 80]; break
    if 'CFI' not in out:
        for m in CFI_BARE.finditer(t):
            win = t[max(0, m.start() - 200):m.end() + 200]
            if CANADA_CTX.search(win) and not NOT_CFI.search(win):
                out['CFI'] = t[max(0, m.start() - 80):m.end() + 80]; break
        else:
            for m in FCI_BARE.finditer(t):
                win = t[max(0, m.start() - 200):m.end() + 200]
                if re.search(r'Fondation|Canad|Qu[ée]bec', win, I):
                    out['CFI'] = t[max(0, m.start() - 80):m.end() + 80]; break
    return out
def extract(xml):
    try:
        root = ET.fromstring(xml)
    except ET.ParseError:
        xml2 = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;|#)', '&amp;', xml)
        root = ET.fromstring(xml2)
    parts, conflict = [], []
    hdr = root.find(f'{NS}teiHeader')
    funders = [tx(f) for f in (hdr.iter(f'{NS}funder') if hdr is not None else [])]
    text_el = root.find(f'{NS}text')
    seen = set()
    if text_el is not None:
        for d in text_el.iter(f'{NS}div'):
            ty = d.get('type')
            if ty in ('acknowledgement', 'funding'):
                parts.append(tx(d)); seen.update(id(x) for x in d.iter())
            elif ty == 'conflict':
                conflict.append(tx(d)); seen.update(id(x) for x in d.iter())
        for d in text_el.iter(f'{NS}div'):
            if id(d) in seen: continue
            h = d.find(f'{NS}head')
            if h is not None and HEAD_RE.search(tx(h) or '') and not re.search(r'conflict|competing|interest', tx(h), I):
                parts.append(tx(d)); seen.update(id(x) for x in d.iter())
    for n in root.iter(f'{NS}note'):
        if n.get('place') == 'foot' and id(n) not in seen:
            t = tx(n)
            if NOTE_RE.search(t) and not re.search(r'conflict of interest|competing interest', t, I): parts.append(t)
    ack = ' || '.join(p for p in parts if p)
    # broad text: body + back minus references and conflict
    broad = []
    if text_el is not None:
        skip = set(seen_conf for seen_conf in ())
        for el in text_el.iter():
            if el.tag in (f'{NS}listBibl',) or (el.tag == f'{NS}div' and el.get('type') in ('references', 'conflict')):
                skip.update(id(x) for x in el.iter())
        for s in text_el.iter():
            if id(s) in skip: continue
            if s.tag in (f'{NS}s', f'{NS}note') or (s.tag == f'{NS}p' and s.find(f'{NS}s') is None):
                broad.append(tx(s))
    return ack, ' '.join(funders), ' || '.join(conflict), broad
rows = []; texts = []
cand = {r['work_id']: r for r in csv.DictReader(open(f'{HERE}/candidates.csv'))}
for p in sorted(glob.glob(f'{CACHE}/*.xml.gz')):
    wid = os.path.basename(p).split('.')[0]
    if wid not in cand: continue
    xml = gzip.open(p, 'rt', encoding='utf-8', errors='ignore').read()
    c = cand[wid]
    try:
        ack, fund_hdr, conflict, broad = extract(xml)
        perr = ''
    except Exception as e:
        ack, fund_hdr, conflict, broad, perr = '', '', '', [], repr(e)[:60]
    acktext = (ack + ' || ' + fund_hdr).strip(' |')
    hits = tri_hits(acktext)
    anyhits = {}
    for s in broad:
        if SUPPORT.search(s):
            for ag, snip in tri_hits(s).items(): anyhits.setdefault(ag, snip)
    conf_hits = tri_hits(conflict)
    crc = CRC.search(acktext); oth = OTHER.search(acktext)
    rows.append({**{k: c[k] for k in ('stratum', 'rank', 'work_id', 'year', 'first_author_cn_only', 'oa_status', 'field_tri_local', 'field_tri_live')},
                 'tei_bytes': len(xml), 'parse_err': perr, 'usable': int(len(acktext) >= 20),
                 'ack_len': len(acktext), 'ack_tri': int(bool(hits)), 'ack_agencies': '|'.join(sorted(hits)),
                 'any_tri_ctx': int(bool(hits) or bool(anyhits)), 'any_agencies': '|'.join(sorted(set(hits) | set(anyhits))),
                 'conflict_only_tri': int(bool(conf_hits) and not hits),
                 'crc': int(bool(crc)), 'other_cdn_program': oth.group(0) if oth else '',
                 'snippet': ' ... '.join(hits.values())[:400], 'any_snippet': ' ... '.join(v for k, v in anyhits.items() if k not in hits)[:300]})
    texts.append({'work_id': wid, 'ack': acktext, 'conflict': conflict})
with open(f'{HERE}/works.csv', 'w', newline='') as fh:
    wr = csv.DictWriter(fh, fieldnames=list(rows[0])); wr.writeheader(); wr.writerows(rows)
with open(f'{HERE}/acks.jsonl', 'w') as fh:
    for t in texts: fh.write(json.dumps(t, ensure_ascii=False) + '\n')
print(len(rows), 'works;', sum(r['usable'] for r in rows), 'usable;', sum(1 for r in rows if r['parse_err']), 'parse errors')
