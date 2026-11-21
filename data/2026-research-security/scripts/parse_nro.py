"""Parse the Named Research Organizations list HTML into JSON (list_name, country, aliases)."""
import re, html, json, sys
src = sys.argv[1]; out = sys.argv[2]
t = open(src, encoding='utf-8').read()
mod = re.search(r'dateModified">([\d-]+)', t)
t = re.sub(r'<script.*?</script>|<style.*?</style>', '', t, flags=re.S)
t = re.sub(r'<br\s*/?>|</(p|li|tr|td|th|h\d|div|dt|dd)>', '\n', t)
t = html.unescape(re.sub(r'<[^>]+>', '', t))
lines = [l.strip() for l in t.split('\n') if l.strip()]
start = lines.index('Named Research Organizations List')
CMAP = {"People’s Republic of China": 'CN', 'Iran': 'IR', 'Russia': 'RU'}
ents = []
for l in lines[start:]:
    if l.startswith('Date modified'): break
    m = re.match(r'^(.*)\((People’s Republic of China|Iran|Russia)\s*\)$', l)
    if m:
        ents.append({'list_name': m.group(1).strip(), 'country': CMAP[m.group(2)], 'aliases': []})
    elif l.startswith('Known alias(es):') and ents:
        ents[-1]['aliases'] = [a.strip() for a in re.split(r';', l.split(':', 1)[1]) if a.strip()]
json.dump({'date_modified': mod.group(1) if mod else None, 'entries': ents}, open(out, 'w'), indent=1, ensure_ascii=False)
from collections import Counter
print(len(ents), Counter(e['country'] for e in ents), mod.group(1) if mod else None)
