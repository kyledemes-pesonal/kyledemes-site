"""Read-only SQL with EXTERNAL_LINKS + CSV disposition for large results (presigned chunk URLs).
Usage: python dbx_big.py <query.sql> <out.csv>"""
import json, subprocess, sys, time, urllib.request, os
sys.path.insert(0, os.path.dirname(__file__))
from dbx import call, W
q = open(sys.argv[1]).read()
q = '\n'.join(x for x in q.splitlines() if not x.strip().startswith('--'))
assert q.strip().split()[0].upper() in ('SELECT', 'WITH'), 'read-only queries only'
r = call('post', '/api/2.0/sql/statements', {'statement': q, 'warehouse_id': W, 'wait_timeout': '50s',
                                              'disposition': 'EXTERNAL_LINKS', 'format': 'CSV'})
sid, t0 = r['statement_id'], time.time()
print('statement', sid, flush=True)
while r['status']['state'] in ('PENDING', 'RUNNING'):
    if time.time() - t0 > int(os.environ.get('DBX_TIMEOUT', '7200')): raise RuntimeError('timeout')
    time.sleep(15); r = call('get', '/api/2.0/sql/statements/' + sid)
if r['status']['state'] != 'SUCCEEDED': raise RuntimeError(json.dumps(r['status'])[:800])
m = r['manifest']; n = m.get('total_chunk_count', 0)
print('rows', m.get('total_row_count'), 'chunks', n, f'{time.time()-t0:.0f}s', flush=True)
with open(sys.argv[2], 'wb') as out:
    out.write((','.join(c['name'] for c in m['schema']['columns']) + '\n').encode())
    for i in range(n):
        c = call('get', f'/api/2.0/sql/statements/{sid}/result/chunks/{i}')
        for link in c.get('external_links', []):
            data = urllib.request.urlopen(link['external_link'], timeout=600).read()
            lines = data.split(b"\n"); hdr = lines[0].startswith(m["schema"]["columns"][0]["name"].encode()); data = b"\n".join(lines[1:] if hdr else lines)
            out.write(data if data.endswith(b"\n") or not data else data + b"\n")
print('done', sys.argv[2])
