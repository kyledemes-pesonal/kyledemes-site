"""Draw the five charts in the post as Claude Docs chart modules (figures/*.jsx); figures/*.png are renders of them.
Run after analyse.py and awards_flow.py. Every number a chart shows is read from results/ and embedded as rows."""
import charts as c

c.TITLES['funnel'] = 'When a paper names OpenAlex in its abstract, the authors used it 9 times in 10;|when it names OpenAlex only in the body text, 6 times in 10'
c.SUBS['funnel'] = 'Works in OpenAlex that say \u201cOpenAlex\u201d or cite the OpenAlex paper, by where the word appears|Each bar is 100% of its group'
c.funnel(drop_unread=True, slug='mentions-sorted-v2', name='1-mentions')           # chart 1
c.years()                                                                            # chart 2 (figures/used_by_year.jsx)
c.dots('countries-use-vs-output', c.countries(),                                     # chart 3
       'Dutch, Swiss, German and Canadian researchers use OpenAlex at about twice their|share of the world\u2019s research; Chinese and Indonesian researchers, well under theirs',
       'Share of papers that used OpenAlex vs share of all research papers, by author country, 2022 to 2026|Top 15 countries by number of papers that used OpenAlex',
       'Papers that used OpenAlex (3,568 with a known author country)', 'All research papers, 2022 to 2026 (33.5 million with a known country)', 'All papers',
       'A paper counts once for each country among its authors. Shares are of papers with at least one known author country.')
c.dots('fields-use-vs-output', c.fields(),                                           # chart 4
       'Social science and computer science papers use OpenAlex at more than twice|their share of research; engineering, medicine and the humanities, far less',
       'Share of papers that used OpenAlex vs share of all research papers, by field of main topic, 2022 to 2026|Library and information science alone is 31% of the papers that used OpenAlex',
       'Papers that used OpenAlex (4,672)', 'All research papers, 2022 to 2026 (51.9 million with a field)', 'All papers',
       'Fields as OpenAlex assigns them from each paper\u2019s main topic. Top 12 fields by papers that used OpenAlex.')
c.bowtie()                                                                           # chart 5 (figures/who_pays_flow.jsx)
