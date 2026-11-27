"""Read-only SQL against the OpenAlex Databricks warehouse through the signed-in CLI (statements API)."""
import json, os, subprocess, sys, time
# Published copy: the SQL warehouse ID comes from the environment (set DATABRICKS_WAREHOUSE_ID); the
# Databricks CLI must already be signed in. The original run used OpenAlex's internal warehouse.
W = os.environ.get('DATABRICKS_WAREHOUSE_ID', '')
def call(method, path, body=None):
    cmd = ['databricks', 'api', method, path] + (['--json', json.dumps(body)] if body is not None else [])
    out = subprocess.run(cmd, capture_output=True, text=True)
    txt = out.stdout[out.stdout.find('{'):] if '{' in out.stdout else out.stdout
    if out.returncode != 0:
        raise RuntimeError((out.stderr or out.stdout)[:500])
    return json.loads(txt)
def sql(q, timeout_s=int(__import__("os").environ.get("DBX_TIMEOUT", "900"))):
    q = '\n'.join(x for x in q.splitlines() if not x.strip().startswith('--'))
    assert q.strip().split()[0].upper() in ('SELECT', 'WITH', 'DESCRIBE', 'SHOW'), 'read-only queries only'
    r = call('post', '/api/2.0/sql/statements', {'statement': q, 'warehouse_id': W, 'wait_timeout': '50s',
                                                  'disposition': 'INLINE', 'format': 'JSON_ARRAY'})
    sid, t0 = r['statement_id'], time.time()
    while r['status']['state'] in ('PENDING', 'RUNNING'):
        if time.time() - t0 > timeout_s:
            raise RuntimeError('timeout')
        time.sleep(5)
        r = call('get', '/api/2.0/sql/statements/' + sid)
    if r['status']['state'] != 'SUCCEEDED':
        raise RuntimeError(json.dumps(r['status'])[:600])
    cols = [c['name'] for c in r['manifest']['schema']['columns']]
    rows = (r.get('result') or {}).get('data_array') or []
    nxt = (r.get('result') or {}).get('next_chunk_internal_link')
    while nxt:
        c = call('get', nxt)
        rows += c.get('data_array') or []
        nxt = c.get('next_chunk_internal_link')
    return cols, rows
if __name__ == '__main__':
    cols, rows = sql(open(sys.argv[1]).read() if sys.argv[1].endswith('.sql') else sys.argv[1])
    if len(sys.argv) > 2:
        json.dump({'cols': cols, 'rows': rows}, open(sys.argv[2], 'w'), ensure_ascii=False)
    print(cols)
    for r in rows[:40]:
        print([str(x)[:120] for x in r])
    print(len(rows), 'rows')
