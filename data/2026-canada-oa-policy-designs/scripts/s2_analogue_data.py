"""Step 2 data: OA routes by year (2004-2025) for 16 high-income countries, 22 funders, UiT vs Norway."""
from oa import *
Y = 'publication_year:2004-2025'
HI = ['CA','US','GB','NL','DE','FR','SE','NO','FI','CH','AT','AU','JP','ES','IT','KR']
FUND = {'Tri-agency': TRI, 'CIHR': AG['cihr'], 'NSERC': AG['nserc'], 'SSHRC': AG['sshrc'],
 'NIH': 'F4320332161', 'Wellcome': 'F4320311904', 'UKRI+councils': 'F4320314731|F4320334626|F4320334627', 'NWO': 'F4320321800',
 'ANR': 'F4320320883', 'FWF': 'F4320321181', 'SNSF': 'F4320320924', 'DFG': 'F4320320879', 'NSF': 'F4320306076',
 'European Commission': 'F4320320300', 'ERC': 'F4320338335', 'NHMRC': 'F4320334705', 'ARC': 'F4320334704',
 'JSPS': 'F4320334764', 'RCN Norway': 'F4320323299', 'VR Sweden': 'F4320322581', 'Formas': 'F4320321033',
 'Gates': 'F4320306137', 'HHMI': 'F4320306082'}
sets = {**{f'country:{c}': f'institutions.country_code:{c}' for c in HI},
        **{f'funder:{k}': f'funders.id:{v}' for k, v in FUND.items()},
        'inst:UiT': 'institutions.id:I78037679',
        'inst:NO_not_UiT': 'institutions.country_code:NO,institutions.id:!I78037679'}
out = {}
for name, f in sets.items():
    base = f'{BASE},{Y},{f}'
    out[name] = {'routes': by_year_route(base), 'anyrepo': by_year(base + ',open_access.any_repository_has_fulltext:true')}
    print(name)
save('s2_analogue_sets.json', out)
