"""Funded slice vs national output, 2025 and 2015: funder papers with an author in the funder's country, as a share of the
country's papers, and their free-to-read share against the country's."""
from oa import *
PAIRS = {'Tri-agency': (TRI, 'CA'), 'UKRI+councils': ('F4320314731|F4320334626|F4320334627', 'GB'), 'Wellcome': ('F4320311904', 'GB'),
         'NIH': ('F4320332161', 'US'), 'NSF': ('F4320306076', 'US'), 'NWO': ('F4320321800', 'NL'), 'DFG': ('F4320320879', 'DE'),
         'FWF': ('F4320321181', 'AT'), 'SNSF': ('F4320320924', 'CH'), 'ANR': ('F4320320883', 'FR'),
         'NHMRC+ARC': ('F4320334705|F4320334704', 'AU'), 'RCN Norway': ('F4320323299', 'NO'), 'VR Sweden': ('F4320322581', 'SE'),
         'JSPS': ('F4320334764', 'JP')}
out = {}
for k, (f, c) in PAIRS.items():
    out[k] = {'country': c}
    for y in (2015, 2025):
        b = f'{BASE},publication_year:{y},institutions.country_code:{c}'
        nat, nat_open = count(b), count(b + ',is_oa:true')
        fu, fu_open = count(b + f',funders.id:{f}'), count(b + f',funders.id:{f},is_oa:true')
        out[k][y] = {'national': nat, 'national_open': nat_open, 'funded': fu, 'funded_open': fu_open}
    v = out[k][2025]
    print(f"{k:14s} {c} funded share {100*v['funded']/v['national']:.1f}% | funded open {100*v['funded_open']/v['funded']:.1f} vs national {100*v['national_open']/v['national']:.1f} | non-funded {100*(v['national_open']-v['funded_open'])/(v['national']-v['funded']):.1f}")
save('s2_funded_vs_national.json', out)
