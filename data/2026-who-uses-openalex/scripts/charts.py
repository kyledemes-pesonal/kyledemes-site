"""Write the Claude Docs chart widgets (one-line JSX modules) from results/summary.json into figures/*.jsx.
Every number on a chart comes from the rows embedded in its module; titles and notes are the only typed words."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
RES, FIG = os.path.join(HERE, '..', 'results'), os.path.join(HERE, '..', 'figures')
S = json.load(open(os.path.join(RES, 'summary.json')))
CNAME = {'US': 'United States', 'DE': 'Germany', 'BR': 'Brazil', 'ES': 'Spain', 'CA': 'Canada', 'ID': 'Indonesia',
         'RU': 'Russia', 'NL': 'Netherlands', 'FR': 'France', 'GB': 'United Kingdom', 'CN': 'China', 'IN': 'India',
         'IT': 'Italy', 'CH': 'Switzerland', 'PH': 'Philippines', 'SE': 'Sweden', 'MX': 'Mexico', 'BE': 'Belgium',
         'PL': 'Poland', 'AU': 'Australia', 'JP': 'Japan', 'PT': 'Portugal', 'AT': 'Austria', 'CO': 'Colombia',
         'TR': 'Türkiye', 'KR': 'South Korea', 'EC': 'Ecuador', 'SA': 'Saudi Arabia', 'MY': 'Malaysia', 'NG': 'Nigeria',
         'ZA': 'South Africa', 'PE': 'Peru', 'AR': 'Argentina', 'CL': 'Chile', 'NO': 'Norway', 'DK': 'Denmark',
         'FI': 'Finland', 'IE': 'Ireland', 'PK': 'Pakistan', 'IR': 'Iran', 'UA': 'Ukraine', 'RO': 'Romania',
         'GR': 'Greece', 'CZ': 'Czechia', 'HU': 'Hungary', 'SI': 'Slovenia', 'HR': 'Croatia', 'RS': 'Serbia',
         'VN': 'Vietnam', 'TH': 'Thailand', 'EG': 'Egypt', 'KE': 'Kenya', 'NZ': 'New Zealand', 'IL': 'Israel',
         'TW': 'Taiwan', 'SG': 'Singapore', 'HK': 'Hong Kong', 'BD': 'Bangladesh', 'UY': 'Uruguay', 'CU': 'Cuba',
         'VE': 'Venezuela', 'LT': 'Lithuania', 'EE': 'Estonia', 'LV': 'Latvia', 'SK': 'Slovakia', 'BG': 'Bulgaria',
         'KZ': 'Kazakhstan', 'MA': 'Morocco', 'TN': 'Tunisia', 'DZ': 'Algeria', 'GH': 'Ghana', 'ET': 'Ethiopia',
         'LU': 'Luxembourg', 'CR': 'Costa Rica', 'AE': 'United Arab Emirates', 'QA': 'Qatar', 'JO': 'Jordan',
         'IQ': 'Iraq', 'LB': 'Lebanon', 'NP': 'Nepal', 'LK': 'Sri Lanka', 'TZ': 'Tanzania', 'UG': 'Uganda'}


TITLES = {
    'years': 'Papers that used OpenAlex have more than doubled every year;|in 2026, reviews that search it took off',
    'funnel': 'When OpenAlex is named in the abstract, the authors almost always used it;|when it is named only in the body, about half the time',
}
SUBS = {
    'years': 'Research papers that used OpenAlex data, by year published, and how many used it to find studies for a review',
    'funnel': 'Every work in OpenAlex that says \"OpenAlex\" or cites the OpenAlex paper, by where the word appears|Each bar is 100% of its group',
}


def js(rows):
    return json.dumps(rows, ensure_ascii=False).replace('"', "'")


def write(name, code):
    os.makedirs(FIG, exist_ok=True)
    open(os.path.join(FIG, name + '.jsx'), 'w').write(code)
    print(name, len(code))


def years():
    """Stacked bars: papers that used OpenAlex by year, reviews that searched it (accent) under all other uses (grey)."""
    import csv, collections
    rows_c = list(csv.DictReader(open(os.path.join(RES, 'corpus.csv'))))
    c = collections.Counter((r['publication_year'], r['use'] == 'literature_search') for r in rows_c)
    rows = []
    for y in sorted({r['publication_year'] for r in rows_c}):
        rows.append({'year': y, 'series': 'Searched it for a review', 'slug': 'reviews', 'papers': c[(y, True)]})
        rows.append({'year': y, 'series': 'All other uses', 'slug': 'other', 'papers': c[(y, False)]})
    head, hy, aria = header(TITLES['years'], SUBS['years'])
    y0, h = hy + 70, 240
    code = ("export default () => <claude.Visualize data-claude-component='used-by-year' sources={{rows:{kind:'data', data:" + js(rows) + "}}}>{({rows, datum}) => { "
            "const left = 60, y0 = " + str(y0) + ", h = " + str(h) + ", w = 660; "
            "const years = [...new Set(rows.map(r => r.year))]; "
            "const tot = yr => rows.filter(r => r.year === yr).reduce((s, r) => s + r.papers, 0); "
            "const peak = Math.max(...years.map(tot)); "
            "const band = w / years.length, bw = band * 0.5, x = i => left + i * band + (band - bw) / 2, hh = v => v / peak * h; "
            "return <svg viewBox='0 0 760 " + str(y0 + h + 76) + "' role='img' aria-label='" + aria + "' fontSize='13' fontFamily='inherit'>" + head +
            "<g data-claude-anchor='legend' transform='translate(0," + str(hy) + ")'><rect width='12' height='12' rx='2' fill='var(--cds-chart-categorical-1)'/><text data-claude-text-id='legend-reviews' x='18' y='11' fill='var(--cds-text-secondary)'>Searched OpenAlex for studies to review</text>"
            "<rect x='300' width='12' height='12' rx='2' fill='var(--cds-chart-muted)'/><text data-claude-text-id='legend-other' x='318' y='11' fill='var(--cds-text-secondary)'>All other uses (bibliometrics, datasets, tools ...)</text></g>"
            "<line x1={left} x2={left + w} y1={y0 + h} y2={y0 + h} stroke='var(--cds-chart-axis)'/>"
            "<g data-claude-anchor='bars'>{years.map((yr, i) => { const rv = rows.find(r => r.year === yr && r.slug === 'reviews'), ot = rows.find(r => r.year === yr && r.slug === 'other'); "
            "const a = hh(rv.papers), b = hh(ot.papers), part = yr === '2026'; "
            "return <g key={yr} data-claude-anchor={`year-${yr}`} opacity={part ? 0.75 : 1}>"
            "<rect x={x(i)} y={y0 + h - a} width={bw} height={Math.max(a, 0.5)} fill='var(--cds-chart-categorical-1)' {...datum(rv, 'papers')}><title>{`${yr}: ${rv.papers.toLocaleString('en-US')} papers searched OpenAlex for a review`}</title></rect>"
            "<rect x={x(i)} y={y0 + h - a - b} width={bw} height={Math.max(b - 2, 0.5)} rx='3' fill='var(--cds-chart-muted)' {...datum(ot, 'papers')}><title>{`${yr}: ${ot.papers.toLocaleString('en-US')} papers used it in other ways`}</title></rect>"
            "<text x={x(i) + bw / 2} y={y0 + h - a - b - 8} textAnchor='middle' fontWeight='600' fill='var(--cds-text-primary)'>{tot(yr).toLocaleString('en-US')}</text>"
            "<text x={x(i) + bw / 2} y={y0 + h + 20} textAnchor='middle' fill='var(--cds-text-primary)'>{part ? `${yr}*` : yr}</text>"
            "<text x={x(i) + bw / 2} y={y0 + h + 38} textAnchor='middle' fontSize='12' fill='var(--cds-text-secondary)' {...datum(rv, 'papers')}>{`${rv.papers.toLocaleString('en-US')} reviews`}</text>"
            "</g>; })}</g>"
            "<text data-claude-text-id='note' x='0' y='" + str(y0 + h + 66) + "' fontSize='12' fill='var(--cds-text-secondary)'>* 2026 runs to 24 November. Research papers only; preprint and published versions counted once.</text>"
            "</svg>; }}</claude.Visualize>;")
    write('used_by_year', code)


def funnel(drop_unread=False, slug='mentions-sorted', name='mentions_sorted'):
    g = {}
    for r in S['funnel']:
        g.setdefault(r['group'], {}).setdefault(r['role'], 0)
        g[r['group']][r['role']] += r['works']
    def row(key, label):
        d = g.get(key, {})
        used = sum(d.get(k, 0) for k in ('data_source', 'subject', 'tool'))
        if key == 'body_unread':  # no readable copy: only an abstract that shows use counts; the rest is unknown
            return {'route': label, 'slug': key, 'used': used, 'notused': 0, 'unknown': sum(d.values()) - used}
        return {'route': label, 'slug': key, 'used': used, 'notused': d.get('passing', 0) + d.get('false_positive', 0),
                'unknown': d.get('unclear', 0) + d.get('not_labelled', 0) + d.get(None, 0)}
    rows = [row('title_abstract', 'Names OpenAlex in its title or abstract'),
            row('body_read', 'Names it only in the body (text read)'),
            row('body_unread', 'Names it only in the body (no readable open copy)')]
    if drop_unread:  # v2: the unread group says nothing about use
        rows = rows[:2]
    n = len(rows)
    head, hy, aria = header(TITLES['funnel'], SUBS['funnel'])
    code = ("export default () => <claude.Visualize data-claude-component='" + slug + "' sources={{rows:{kind:'data', data:" + js(rows) + "}}}>{({rows, datum}) => { "
            "const w = 760, y0 = " + str(hy + 50) + ", rh = 84, bh = 24; "
            "const tot = r => r.used + r.notused + r.unknown; "
            "const sx = r => w / tot(r); "
            "return <svg viewBox='0 0 760 " + str(hy + 50 + n * 84 + 30) + "' role='img' aria-label='" + aria + "' fontSize='13' fontFamily='inherit'>" + head +
            "<g data-claude-anchor='legend' transform='translate(0," + str(hy) + ")'><rect width='12' height='12' rx='2' fill='var(--cds-chart-categorical-1)'/><text data-claude-text-id='legend-used' x='18' y='11' fill='var(--cds-text-secondary)'>Used OpenAlex data</text>"
            "<rect x='170' width='12' height='12' rx='2' fill='var(--cds-chart-muted)'/><text data-claude-text-id='legend-mentioned' x='188' y='11' fill='var(--cds-text-secondary)'>Only mentioned it</text>"
            "<rect x='320' width='12' height='12' rx='2' fill='var(--cds-chart-muted)' fillOpacity='0.35'/><text data-claude-text-id='legend-unknown' x='338' y='11' fill='var(--cds-text-secondary)'>Can't tell</text></g>"
            "{rows.map((r, i) => { const yy = y0 + i * rh, k = sx(r), a = r.used * k, b = r.notused * k, c = r.unknown * k, pc = v => Math.round(v / tot(r) * 100); "
            "return <g key={r.slug} data-claude-anchor={`route-${r.slug}`}>"
            "<text x='0' y={yy} fill='var(--cds-text-primary)' fontWeight='600'>{`${r.route}: ${tot(r).toLocaleString('en-US')} works`}</text>"
            "<text x='0' y={yy + 18} fill='var(--cds-text-secondary)'>{[r.used ? `${pc(r.used)}% used it` : '', r.notused ? `${pc(r.notused)}% only mentioned it` : '', r.unknown ? `${pc(r.unknown)}% can't tell` : ''].filter(t => t).join(', ')}</text>"
            "{a > 0 ? <rect x='0' y={yy + 28} width={Math.max(a - 2, 0)} height={bh} rx='3' fill='var(--cds-chart-categorical-1)' {...datum(r, 'used')}><title>{`Used it: ${r.used.toLocaleString('en-US')}`}</title></rect> : null}"
            "{b > 0 ? <rect x={a} y={yy + 28} width={Math.max(b - 2, 0)} height={bh} rx='3' fill='var(--cds-chart-muted)' {...datum(r, 'notused')}><title>{`Only mentioned it: ${r.notused.toLocaleString('en-US')}`}</title></rect> : null}"
            "{c > 0 ? <rect x={a + b} y={yy + 28} width={c} height={bh} rx='3' fill='var(--cds-chart-muted)' fillOpacity='0.35' {...datum(r, 'unknown')}><title>{`Can't tell: ${r.unknown.toLocaleString('en-US')}`}</title></rect> : null}"
            "</g>; })}"
            "<text data-claude-text-id='note' x='0' y='" + str(hy + 50 + n * 84 + 20) + "' fontSize='12' fill='var(--cds-text-secondary)'>All work types, incl. datasets and software. Labels: a language model reading the abstract and each mention.</text>"
            "</svg>; }}</claude.Visualize>;")
    write(name, code)


def header(title, subtitle):
    """Title (17px, bold) and subtitle (13px) as up to two lines each, split on '|'. Returns (svg, next_y, aria)."""
    out, y = [], 24
    for k, line in enumerate(title.split('|')):
        out.append(f"<text data-claude-text-id='title-{k + 1}' x='0' y='{y}' fontSize='17' fontWeight='600' fill='var(--cds-text-primary)'>{line.strip()}</text>")
        y += 22
    y += 2
    for k, line in enumerate(subtitle.split('|')):
        out.append(f"<text data-claude-text-id='subtitle-{k + 1}' x='0' y='{y}' fill='var(--cds-text-secondary)'>{line.strip()}</text>")
        y += 18
    return ''.join(out), y + 8, ' '.join(l.strip() for l in title.split('|'))


def dots(slug, rows, title, subtitle, a_name, b_name, col_b, note):
    """Dot plot: one row per item, blue dot = share among papers that used OpenAlex, grey dot = comparison share.
    rows: [{'label','slug','a','b'}] with shares as fractions; values shown in two columns on the right."""
    head, hy, aria = header(title, subtitle)
    y0 = hy + 64
    H = y0 + 26 * len(rows) + 30
    code = ("export default () => <claude.Visualize data-claude-component='" + slug + "' sources={{rows:{kind:'data', data:" + js(rows) + "}}}>{({rows, datum}) => { "
            "const lx = 184, rx = 560, y0 = " + str(y0) + ", rh = 26, peak = Math.max(...rows.map(r => Math.max(r.a, r.b))); "
            "const x = v => lx + v / peak * (rx - lx), pct = v => `${(v * 100).toFixed(1)}%`; "
            "return <svg viewBox='0 0 760 " + str(H) + "' role='img' aria-label='" + aria + "' fontSize='13' fontFamily='inherit'>" + head +
            "<g data-claude-anchor='legend' transform='translate(0," + str(hy) + ")'><circle cx='6' cy='6' r='6' fill='var(--cds-chart-categorical-1)'/><text data-claude-text-id='legend-a' x='18' y='11' fill='var(--cds-text-secondary)'>" + a_name + "</text>"
            "<circle cx='6' cy='28' r='5.5' fill='var(--cds-chart-muted)'/><text data-claude-text-id='legend-b' x='18' y='33' fill='var(--cds-text-secondary)'>" + b_name + "</text></g>"
            "<text data-claude-text-id='col-a' x='660' y='" + str(y0 - 14) + "' textAnchor='end' fontWeight='600' fill='var(--cds-text-primary)'>Used OpenAlex</text>"
            "<text data-claude-text-id='col-b' x='752' y='" + str(y0 - 14) + "' textAnchor='end' fontWeight='600' fill='var(--cds-text-secondary)'>" + col_b + "</text>"
            "<g data-claude-anchor='rows'>{rows.map((r, i) => { const yy = y0 + i * rh + 8; return <g key={r.slug} data-claude-anchor={`row-${r.slug}`}>"
            "<line x1={lx} x2={rx} y1={yy} y2={yy} stroke='var(--cds-chart-grid)'/>"
            "<line x1={x(Math.min(r.a, r.b))} x2={x(Math.max(r.a, r.b))} y1={yy} y2={yy} stroke='var(--cds-chart-muted)' strokeWidth='2'/>"
            "<text x={lx - 10} y={yy + 4} textAnchor='end' fill='var(--cds-text-primary)'>{r.label}</text>"
            "<circle cx={x(r.b)} cy={yy} r='5.5' fill='var(--cds-chart-muted)' {...datum(r, 'b')}><title>{`${r.label}, " + col_b.lower() + ": ${pct(r.b)}`}</title></circle>"
            "<circle cx={x(r.a)} cy={yy} r='6' fill='var(--cds-chart-categorical-1)' {...datum(r, 'a')}><title>{`${r.label}, papers that used OpenAlex: ${pct(r.a)}`}</title></circle>"
            "<text x='660' y={yy + 4} textAnchor='end' fontWeight='600' fill='var(--cds-text-primary)' {...datum(r, 'a')}>{pct(r.a)}</text>"
            "<text x='752' y={yy + 4} textAnchor='end' fill='var(--cds-text-secondary)' {...datum(r, 'b')}>{pct(r.b)}</text>"
            "</g>; })}</g>"
            "<text data-claude-text-id='note' x='0' y='" + str(H - 10) + "' fontSize='12' fill='var(--cds-text-secondary)'>" + note + "</text>"
            "</svg>; }}</claude.Visualize>;")
    write(slug, code)


def countries():
    rows = [{'label': CNAME.get(c['country'], c['country']), 'slug': c['country'].lower(),
             'a': c['share_of_corpus_with_country'], 'b': c['share_of_all_papers_with_country']} for c in S['countries'][:15]]
    return rows


SHORT_FIELD = {'Social Sciences': 'Social sciences', 'Computer Science': 'Computer science',
               'Business, Management and Accounting': 'Business and management', 'Decision Sciences': 'Decision sciences',
               'Environmental Science': 'Environmental science', 'Economics, Econometrics and Finance': 'Economics and finance',
               'Agricultural and Biological Sciences': 'Agriculture and biology', 'Arts and Humanities': 'Arts and humanities',
               'Health Professions': 'Health professions'}


def fields():
    rows = [{'label': SHORT_FIELD.get(f['field'], f['field']), 'slug': f['field'].lower().replace(',', '').replace(' ', '-'),
             'a': f['share_of_corpus'], 'b': f['share_of_all_papers']} for f in S['fields'] if f['field'] != 'Unknown'][:12]
    return rows


def pays():
    rows = [{'label': CNAME.get(r['country'], r['country']), 'slug': r['country'].lower(),
             'a': r['share_of_using_papers'], 'b': r['share_of_paying_institutions']} for r in S['pays_vs_uses']]
    rows = sorted(rows, key=lambda r: -max(r['a'], r['b']))[:14]
    return rows


if __name__ == '__main__':
    years()
    funnel()


def bowtie():
    """Flow chart: OpenAlex's money in (left, share of revenue) and the grants behind the research that uses it
    (right, number of grants by funder). The two sides use different units; the overlap band is the accent."""
    A = json.load(open(os.path.join(RES, 'awards_by_group.json')))
    rows = [
        {'side': 'in', 'slug': 'grants', 'label': 'Grants', 'detail1': 'Arcadia, Wellcome, Navigation', 'detail2': 'Fund, Schmidt Sciences', 'value': 0.56, 'both': False},
        {'side': 'in', 'slug': 'members', 'label': 'Members and customers', 'detail1': '139 listed members, including', 'detail2': '9 research funders', 'value': 0.44, 'both': False},
    ]
    for g in A['groups']:
        lab = g['label'] if g['slug'] != 'other' else f"{g['funders']} other funders"
        rows.append({'side': 'out', 'slug': g['slug'], 'label': lab, 'detail1': '', 'detail2': '', 'value': g['grants'], 'both': g['slug'] == 'both'})
    head, hy, aria = header('Funders that pay for OpenAlex are behind 5% of the grants|on the research that uses it',
                            'Left: where OpenAlex’s money comes from. Right: grants listed on papers that used OpenAlex|The sides use different units: share of revenue on the left, number of grants on the right')
    yT, H, gl, gr = hy + 44, 340, 16, 6
    n_out = sum(1 for r in rows if r['side'] == 'out')
    Hsvg = yT + H + gr * (n_out - 1) + 70
    code = ("export default () => <claude.Visualize data-claude-component='who-pays-flow' sources={{rows:{kind:'data', data:" + js(rows) + "}}}>{({rows, datum}) => { "
            "const yT = " + str(yT) + ", H = " + str(H) + ", gl = " + str(gl) + ", gr = " + str(gr) + "; "
            "const ins = rows.filter(r => r.side === 'in'), outs = rows.filter(r => r.side === 'out'); "
            "const T = outs.reduce((s, r) => s + r.value, 0), k = H / T, mid = yT + (gr * (outs.length - 1)) / 2; "
            "let ly = mid - gl / 2, lc = mid; const L = ins.map(r => { const h = r.value * H; const o = {r, y: ly, c: lc, h}; ly += h + gl; lc += h; return o; }); "
            "let ry = yT, rc = mid; const R = outs.map(r => { const h = r.value * k; const o = {r, y: ry, c: rc, h}; ry += h + gr; rc += h; return o; }); "
            "const band = (x0, y0, x1, y1, h) => { const xm = (x0 + x1) / 2; return `M${x0},${y0} C${xm},${y0} ${xm},${y1} ${x1},${y1} L${x1},${y1 + h} C${xm},${y1 + h} ${xm},${y0 + h} ${x0},${y0 + h} Z`; }; "
            "const both = outs.filter(r => r.both).reduce((s, r) => s + r.value, 0); "
            "return <svg viewBox='0 0 760 " + str(Hsvg) + "' role='img' aria-label='" + aria + "' fontSize='13' fontFamily='inherit'>" + head +
            "<text data-claude-text-id='head-left' x='0' y='" + str(yT - 14) + "' fontWeight='600' fill='var(--cds-text-primary)'>Who pays for OpenAlex</text>"
            "<text data-claude-text-id='head-right' x='484' y='" + str(yT - 14) + "' fontWeight='600' fill='var(--cds-text-primary)'>Who pays for the research that uses it</text>"
            "<g data-claude-anchor='money-in'>{L.map(o => <g key={o.r.slug} data-claude-anchor={`in-${o.r.slug}`}>"
            "<path d={band(212, o.y, 330, o.c, o.h)} fill='var(--cds-chart-muted)' fillOpacity='0.45' {...datum(o.r, 'value')}><title>{`${o.r.label}: about ${Math.round(o.r.value * 100)}% of OpenAlex’s revenue`}</title></path>"
            "<rect x='200' y={o.y} width='12' height={o.h} rx='2' fill='var(--cds-chart-muted)' {...datum(o.r, 'value')}/>"
            "<text x='190' y={o.y + o.h / 2 - 10} textAnchor='end' fontWeight='600' fill='var(--cds-text-primary)'>{o.r.label}</text>"
            "<text x='190' y={o.y + o.h / 2 + 8} textAnchor='end' fontSize='12' fill='var(--cds-text-secondary)'>{o.r.detail1}</text>"
            "<text x='190' y={o.y + o.h / 2 + 24} textAnchor='end' fontSize='12' fill='var(--cds-text-secondary)'>{o.r.detail2}</text></g>)}</g>"
            "<rect x='330' y={mid} width='16' height={H} rx='3' fill='var(--cds-text-primary)'/>"
            "<text data-claude-text-id='center' x='338' y={mid - 10} textAnchor='middle' fontWeight='700' fill='var(--cds-text-primary)'>OpenAlex</text>"
            "<g data-claude-anchor='grants-out'>{R.map(o => <g key={o.r.slug} data-claude-anchor={`out-${o.r.slug}`}>"
            "<path d={band(346, o.c, 470, o.y, o.h)} fill={o.r.both ? 'var(--cds-chart-categorical-1)' : 'var(--cds-chart-muted)'} fillOpacity={o.r.both ? 0.75 : 0.45} {...datum(o.r, 'value')}><title>{`${o.r.label}: ${o.r.value.toLocaleString('en-US')} grants`}</title></path>"
            "<rect x='470' y={o.y} width='8' height={o.h} rx='2' fill={o.r.both ? 'var(--cds-chart-categorical-1)' : 'var(--cds-chart-muted)'} {...datum(o.r, 'value')}/>"
            "<text x='486' y={o.y + o.h / 2 + 4} fontWeight={o.r.both ? 600 : 400} fill='var(--cds-text-primary)' {...datum(o.r, 'value')}>{`${o.r.label} · ${o.r.value.toLocaleString('en-US')}`}</text></g>)}</g>"
            "<text x='484' y={yT + H + gr * (outs.length - 1) + 20} fontSize='12' fill='var(--cds-text-secondary)'>{`${T.toLocaleString('en-US')} grants in all, ${Math.round(both / T * 100)}% in blue`}</text>"
            "<text data-claude-text-id='note-1' x='0' y='" + str(Hsvg - 26) + "' fontSize='12' fill='var(--cds-text-secondary)'>Also paying: Portugal’s FCT, Wellcome, Dutch, Swedish and Chilean research councils, Japan’s JST, Austria’s FWF.</text>"
            "<text data-claude-text-id='note-2' x='0' y='" + str(Hsvg - 8) + "' fontSize='12' fill='var(--cds-text-secondary)'>Left: US tax filing, year to June 2025. Right: each grant counts once, whatever its size.</text>"
            "</svg>; }}</claude.Visualize>;")
    write('who_pays_flow', code)
