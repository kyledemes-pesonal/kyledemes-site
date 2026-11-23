"""Step 1 data: Canadian papers, tri-agency slice, routes, repository copies, full-text split. 2010-2025."""
from oa import *
Y = 'publication_year:2010-2025'
CA = 'institutions.country_code:CA'
REPO = carepo_filter()
out = {}
sets = {'canada': CA, 'tri_ca': f'{CA},funders.id:{TRI}',
        **{f'{k}_ca': f'{CA},funders.id:{v}' for k, v in AG.items()},
        'tri_any': f'funders.id:{TRI}'}
for name, f in sets.items():
    base = f'{BASE},{Y},{f}'
    out[name] = {'routes': by_year_route(base),
                 'carepo': by_year(base + ',' + REPO),
                 'anyrepo': by_year(base + ',open_access.any_repository_has_fulltext:true'),
                 'fulltext_true': by_year(base + ',has_fulltext:true'),
                 'fulltext_true_open': by_year(base + ',has_fulltext:true,is_oa:true'),
                 'fulltext_false_open': by_year(base + ',has_fulltext:false,is_oa:true'),
                 'with_award': by_year(base + f',awards.funder_id:{TRI}') if name.startswith('tri') else {}}
    print(name, 'done')
save('s1_canada_sets.json', out)
