"""Shared definitions (v2, 24 Nov 2026, after the verification pass).
Nordic = Denmark, Finland, Iceland, Norway, Sweden, Greenland, Faroe Islands, Aland.
Arctic and northern research = title or abstract names an Arctic place, people or feature (TERMS); permafrost and tundra
only count when the paper doesn't name the Tibetan Plateau, Himalaya or northern China.
Sami: a bare "sami" matches the given name Sami and Croatian "sami" (the search ignores accents), so Sami research is found
through saami, sapmi, or sami together with reindeer, indigenous, Norway, Sweden or Finland.
v1 (defs_v1.py) had 21 terms and no Sami, Nordic or Russian/Alaskan Arctic place names and no Tibet exclusion."""
NORDIC = 'DK|FI|IS|NO|SE|GL|FO|AX'
TERMS = ['arctic', 'subarctic', 'greenland', 'svalbard', 'nunavut', 'nunavik', 'nunatsiavut', 'inuvialuit',
         'yukon', '"northwest territories"', 'lapland', 'barents', '"beaufort sea"', '"hudson bay"', '"fram strait"',
         'baffin', 'finnmark', 'norrbotten', 'chukchi', 'chukotka', 'yamal', 'taymyr', '"kola peninsula"', '"north slope"',
         'saami', 'sapmi', '(sami AND (reindeer OR indigenous OR norway OR sweden OR finland))',
         # terms that need a guard (verification pass, 24 Nov 2026)
         '(inuit NOT ("first nations" AND metis))',                     # not when only in "First Nations, Inuit and Metis"
         '(circumpolar NOT (antarctic OR antarctica OR "southern ocean"))',  # not the Antarctic Circumpolar Current
         '((permafrost OR tundra) NOT (tibet OR tibetan OR qinghai OR qilian OR himalaya OR himalayan OR tianshan OR '
         '"tian shan" OR "northeast china" OR heilongjiang OR "inner mongolia"))']  # not Tibetan Plateau / northern China
# dropped: "high north" (also matches "high-north to low-south" spatial patterns)
Q = 'title_and_abstract.search:(' + ' OR '.join(TERMS) + ')'

# Priority areas named in Canada-Nordic statements (2017-2026), mapped to OpenAlex: each article's primary topic,
# subfield or field, or the Arctic search. Topic and subfield IDs as of Nov 2026.
AREAS = [
    ('all', 'All articles', None),
    ('arctic', 'The Arctic and the North', Q),
    ('climate', 'Climate and atmosphere', 'primary_topic.subfield.id:1902|2306'),
    ('oceans', 'Oceans and fisheries', 'primary_topic.subfield.id:1910|1104'),
    ('wildfire', 'Wildfire', 'primary_topic.id:T10555'),
    ('indigenous', 'Indigenous health and communities', 'primary_topic.id:T10348|T13822|T12614|T14007'),
    ('mining', 'Mining and mineral processing', 'primary_topic.id:T11091|T11401|T12282|T11933|T13065|T13772'),
    ('mingeo', 'Mineral geology and geochemistry', 'primary_topic.id:T12157|T11740'),
    ('energy', 'Clean energy (incl. nuclear)', 'primary_topic.subfield.id:2105|2104'),
    ('quantum', 'Quantum technologies', 'primary_topic.id:T10020|T10682|T11414'),
    ('ai', 'Artificial intelligence', 'primary_topic.subfield.id:1702'),
    ('connectivity', 'Networks and connectivity', 'primary_topic.subfield.id:1705'),
    ('spacesci', 'Space science (ionosphere and magnetosphere)', 'primary_topic.id:T10159'),
    ('spacetech', 'Space and satellite technology', 'primary_topic.id:T12042|T11701|T11082|T12449|T14214'),
    ('security', 'Security and defence studies', 'primary_topic.id:T14086|T12825|T13369|T14302|T12221|T12432'),
    ('health', 'Medicine (all)', 'primary_topic.field.id:27'),
]
