---
layout: post
title: "Opening old papers barely changed how often they were cited"
date: 2026-11-27 06:00:00 -0700
tags: [open-access]
image: /data/2026-oa-backfile-citations/figures/1-raw-citations.png
image_alt: "Line chart: citations per paper per year for papers whose paywall was removed and for similar papers that stayed closed, 5 years before to 8 years after the opening, across 97 publisher openings. The two lines stay within 1.5 points of each other after the opening."
image_in_post: false
excerpt: "When publishers removed the paywall from old papers, their citations rose by a few percent, below the 18% advantage observational studies find for new papers. Citing and reading seem only loosely connected."
---

Does making a paper free to read cause more people to cite it? Study after study finds that open access papers get cited more. One large analysis found open papers were cited about 18% more than the average paper of the same age and field ([The state of OA, PeerJ, 2018](https://doi.org/10.7717/peerj.4375); [OpenAlex record](https://openalex.org/W2741809807)). But those studies can't rule out the obvious problem: authors choose which papers to make open, and they tend to open their best work.

Another way to look at it, one that's been tried before ([Economic Inquiry, 2014](https://doi.org/10.1111/ecin.12064); [OpenAlex record](https://openalex.org/W3121567788)), is to follow papers whose paywall came off long after they were published. Over the past twenty years, publishers have removed the paywall from old, already-published papers in whole back files at once, on a date the authors didn't choose. If access drives citations, those papers should start getting cited more than similar papers that stayed closed. It isn't a cleaner test, though. Most papers pick up the bulk of their citations in their first few years, so opening a paper ten or twenty years after it came out asks a different question from opening it on the day it appears. A cleaner test would need accurate dates for papers that became free soon after publication, and those are much harder to come by. But it's a method that's been proposed, so it seemed worth exploring.

**The short version: when publishers removed the paywall from old papers, their citations rose by a few percent, below the 18% advantage observational studies find for new papers.** That fits a wider pattern in the literature: citing and reading are only loosely connected.

- Across 113 publisher openings from 2005 to 2024 (about 346,000 papers), opened papers gained between 2% and 7.5% in yearly citations against similar papers that stayed closed, depending on how you weight the journals. The study can't reliably detect effects smaller than about 8 to 11%.
- When about 200 German institutions lost access to new Elsevier papers in 2018 and 2019, their researchers kept citing Elsevier at about the same rate.
- Two randomized trials of free access found more downloads and no more citations.
- Studies of how people cite suggest many citations are copied from other reference lists, misstate their source, or had little influence on the work citing them.

## Did removing the paywall on old papers raise their citations?

**How I looked.** This uses every case that turned up where a publisher removed the paywall from already-published papers, dated from at least one public source: publisher announcements, the licence dates publishers send to Crossref, and archived copies of their web pages. That gave 113 openings between 2005 and 2024 covering about 346,000 papers. The big programs were Elsevier's open archive (its mathematics journals in 2012, and journals joining the archive over the years, counting only the years the archive actually covered), the American Mathematical Society's back files in 2010, Cell Press in 2005 and the Royal Society in 2011, plus one single journal.

I kept only openings where the journal's new papers stayed paywalled, apart from a delay after which later papers would also open. Journals that also flipped their new papers to open access, or moved platforms, were set aside, because any jump in citations could come from the change to the journal rather than from access to old papers.

I also dropped openings that didn't last: archives that later went back behind a paywall when the journal changed publisher or platform within ten years.

For each opening I picked up to five journals in the same subfield that never opened their back files and whose papers were cited at a similar level, and on a similar trend, before the opening. Then I compared yearly citations to the opened papers with citations to papers of the same years in those journals, before and after the opening.

**What stands out.** The two lines stay together after the paywall comes off.

![Line chart of citations per paper per year, indexed to 100 in the year before opening, for papers whose paywall was removed and similar papers that stayed closed, from 5 years before to 8 years after, 97 openings. Both lines rise to 100 and then fall together; the largest gap after opening is 1.5 points.](/data/2026-oa-backfile-citations/figures/1-raw-citations.png)
<p class="figure-source">Source: OpenAlex citations, snapshot of 22 Nov 2026. The 97 of 113 openings observed from 5 years before to 8 years after. Each opening is compared with up to 5 matched journals in the same subfield.</p>

In a model that compares the changes directly, opened papers gained between 2% and 7.5% in yearly citations, depending on the question you ask. Weighted by how much each journal was already cited, the gain is about 2%. Weighted by the number of papers opened, about 4%. Counting each opening equally, which gives small journals more say, about 7.5%. The uncertainty is wide, roughly -4% to +12% for the first, because many journals opened on the same date (about 50 Elsevier mathematics journals in 2012 alone). None of the three is clearly distinguishable from zero. The study can't reliably detect effects smaller than about 8 to 11%. Weighted by citations or by papers opened, the top of the range is about 12%, below 18%; counting each opening equally, the range reaches about 23%, so that weighting can't rule out an 18% gain. So the fair summary is a gain of a few percent.

The answer depends somewhat on which openings are in. Without Cell Press's 2005 opening, the gain weighted by citations is about 4.5% and clearly above zero; without the Elsevier journals that joined its open archive one by one, it is about zero.

One check stands out. In 2023 Annual Reviews opened its new volumes and the nine years of volumes before them, while older volumes of the same journals stayed closed. Inside the same journals, the opened volumes did no better than the closed ones over the two years since (-1.3%).

**Assumptions and caveats.** Most people who cite these papers probably had a way in already: library subscriptions, copies on preprint servers, or Sci-Hub, which has been around since 2011. So this measures what removing the last paywall does, mostly for older papers that most readers could already reach. Only 2.5% of the opened papers had a copy on arXiv before the opening, and those gained no less than the rest, so earlier arXiv copies don't explain it. About half the openings (58 of 113, with 62% of the papers) came from two mathematics programs, Elsevier's in 2012 and the American Mathematical Society's in 2010. Without them the estimates are similar (about 1.5%, or 9.5% counting each opening equally) but much less precise. And OpenAlex is missing reference lists for some of the citing papers (roughly one in eight in a typical year), but the share with lists was within about 2 percentage points for the two groups in every year from 1995 to 2025, and where it differed after 2016 it would hide a small gain, not create one.

## What happens when researchers lose access?

**How I looked.** The mirror image of an opening is a closing. In July 2018, after the German DEAL negotiations broke down, about 180 German institutions lost access to new Elsevier papers, and about 25 more followed in January 2019, until a new agreement was signed in September 2023. A study followed about 400,000 articles by their researchers from 2012 to 2020 ([No deal, Quantitative Science Studies, 2023](https://doi.org/10.1162/qss_a_00255); [OpenAlex record](https://openalex.org/W4362696813)). There are also randomized trials of free access.

**What stands out.** German researchers kept citing Elsevier at about the same rate after losing access.

![Line chart, 2012 to 2020, authors at about 200 German institutions: Elsevier's share of their references to recent papers stays between 23.4% and 25.0% and is 24.0% in 2020, after access was cut in July 2018, while Elsevier's share of their articles falls from 26.3% in 2015 to 20.8% in 2020.](/data/2026-oa-backfile-citations/figures/2-germany-elsevier.png)
<p class="figure-source">Source: "No deal: German researchers' publishing and citing behaviors after Big Deal negotiations with Elsevier", Quantitative Science Studies, 2023, doi 10.1162/qss_a_00255 (OpenAlex W4362696813), which uses Dimensions data. Yearly values from the published version and its data (doi 10.5281/zenodo.7439093).</p>

Elsevier's share of their references to recent papers was 23.4% in 2012, peaked at 25.0% in 2018, and was 24.0% in 2020. The number of citations to Elsevier papers kept rising, from 77,542 in 2016 to 93,035 in 2020. Where they published did shift: Elsevier's share of their articles fell from 26.3% in 2015 to 20.8% in 2020. The study's authors point mainly to other ways of getting the papers; that researchers may cite without reading the full text is, in their words, a "more contentious hypothesis".

The trials point the same way. When a publisher made a random set of its articles free, full-text downloads rose 89%, but the free articles were not cited more after a year ([BMJ, 2008](https://doi.org/10.1136/bmj.a568); [OpenAlex record](https://openalex.org/W1970217003)). A larger trial across 36 journals found the same: more readers, no more citations within three years ([FASEB Journal, 2011](https://doi.org/10.1096/fj.11-183988); [OpenAlex record](https://openalex.org/W2160597895)).

**Assumptions and caveats.** The German study has no comparison group, so it describes what happened rather than proving the cut caused nothing. The fall in publishing with Elsevier started in 2016, as the negotiations began and well before the cut, and the later drop lines up with Germany's open access deals with Wiley (2019) and Springer Nature (2020) and the growth of open access publishers. Many institutions kept access to older Elsevier papers, and the window after the cut is only two and a half years. And in both trials the comparison articles also became free after 6 to 12 months, so the trials compare free now with free a few months later.

## Do people read what they cite?

**How I looked.** If removing a paywall barely changes citations, and losing access barely changes them either, a natural next question is how closely citing is tied to reading at all. A handful of studies measure it.

**What stands out.** A lot of citing happens without close reading.

![Bar chart of four measures from four studies: an estimated 70 to 90% of citations are copied from other reference lists; 54% of citations had little or no influence on the citing work; 16.9 to 25.4% of citations in medical journals misstate the source; 5.4% of citations of retracted papers in biomedicine mention the retraction.](/data/2026-oa-backfile-citations/figures/3-citing-not-reading.png)
<p class="figure-source">Sources: Stochastic modeling of citation slips, Scientometrics 2005 (OpenAlex W1968815786); How status of research papers affects the way they are read and cited, Research Policy 2022 (W4206622121); quotation accuracy meta-analyses, PeerJ 2015 (W1847240671) and Research Integrity and Peer Review 2025 (W4412565252); Continued use of retracted papers, Quantitative Science Studies 2021 (W4200394820).</p>

- A model built from how misprints in references get copied from paper to paper estimates that 70-90% of citations are copied from other reference lists ([Stochastic modeling of citation slips, Scientometrics, 2005](https://doi.org/10.1007/s11192-005-0028-2); [OpenAlex record](https://openalex.org/W1968815786)).
- In a survey of 9,380 authors about 17,154 of their own citations, 54% had little or no influence on the work citing them ([Research Policy, 2022](https://doi.org/10.1016/j.respol.2022.104484); [OpenAlex record](https://openalex.org/W4206622121)).
- In medical journals, 16.9% to 25.4% of citations misstate what the cited paper says, with no improvement over time ([PeerJ, 2015](https://doi.org/10.7717/peerj.1364), [OpenAlex record](https://openalex.org/W1847240671); [Research Integrity and Peer Review, 2025](https://doi.org/10.1186/s41073-025-00173-z), [OpenAlex record](https://openalex.org/W4412565252)).
- In biomedicine, of 13,252 citations made to papers after they were retracted, only 5.4% mention the retraction ([Quantitative Science Studies, 2021](https://doi.org/10.1162/qss_a_00155); [OpenAlex record](https://openalex.org/W4200394820)).

Access still matters for some readers. The strongest study the other way uses Sci-Hub download logs and finds that more Sci-Hub use raised the share of references to paywalled papers by about 7%, mostly to recent papers in highly ranked journals. The shift shows up in high- and middle-income regions; in low-income regions it couldn't be measured (Leveling the playing field, working paper, 2025, now a chapter of a 2026 dissertation; [OpenAlex record](https://openalex.org/W7161360389)). In the back-file data, too, opening up seems to matter more in some places: openings with fewer prior citations gained more (about 7.5% counting each opening equally) than the most-cited ones (about 2%).

**Assumptions and caveats.** These are four different studies, in different fields and years, measuring different things, so the bars don't add up to one number. The copying estimate comes from a model, and the quotation errors and the retraction study are from medicine. None of them is a direct measure of how many citations were made without reading the paper.

## What none of this can tell us

- **Whether open access helps new papers get cited.** These are old papers, opened years after publication, past the years when most of their citations come, and at a time when most readers already had some route in. The 18% figure is about new papers. Papers opened within five years of publication gained about as much as older ones (about 1.4%, with a wide range: -3% to +6%). About 5 in 100 of the opened papers were freed within two years of publication. They don't seem to have gained either, but there are too few of them to rule out a gain of 10 to 20%. So this says little about papers that are open from the day they appear.
- **Whether access matters.** It clearly does for readers: downloads go up when papers are free. Citation counts just aren't a good way to measure it.
- **What happens without Sci-Hub.** Every opening after 2011 happened while Sci-Hub was growing into a click-away copy of most paywalled papers.
- **Effects smaller than about 8 to 11%.** A real gain of 2% or 3% is entirely possible; this design can't tell it from zero.

## Where this leaves me

We already know citations are not a good measure of the quality of research. If removing a paywall barely moves them, and losing access barely moves them either, I think it's probably best to stop treating a citation advantage as a reason to make research open at all. The case for open access is that people can read it, use it and build on it, wherever they are. That case doesn't need citations.

What I didn't expect is how interested I'd get in the other side of this: how many citations are accurate in the first place. I've only scratched the surface here, so I'm going to dig into that literature early in 2027.

## How I did it

- **Openings.** Openings come from publisher announcements, Crossref licence start dates and archived web pages showing a publisher removing the paywall from already-published papers, each dated to the year. 49 openings have two independent date sources; using only those gives a similar answer (about 1%). I set aside openings where the journal also opened its new papers or moved platforms, where a moving wall had already freed older papers, where the journal had moved from another publisher, where only a few article types opened, where the back file was digitized for the first time, where openings overlapped, where the date or range couldn't be pinned down, and openings in 2025 or later. I also set aside openings that later went back behind a paywall within the ten years I follow.
- **Comparison journals.** For each opening, up to five journals in the same OpenAlex subfield that never opened their back files, matched on citation level and trend in the years before.
- **Citations.** OpenAlex citations to each paper by citing year, snapshot of 22 November 2026. I dropped duplicate records (such as JSTOR copies of the same papers) and records filed under the wrong journal, in the opened and comparison journals alike. Counting only citations from journal articles, each counted once, gives a smaller gain: about 1%, or about 5.5% counting each opening equally. Citations from repository papers (preprints, theses) rose more, about 11%.
- **Model.** A Poisson regression comparing changes in yearly citations to opened papers with changes for the comparison papers, from 5 years before to 10 years after, leaving out the opening year itself and comparing papers of the same age. Uncertainty allows for openings that shared a date (14 groups), using a wild bootstrap. I report three weightings: by prior citations, by papers opened, and each opening equally. Before the openings the two groups moved together (a fake opening three years early gives about +1%, -1% to +3%). The chart above shows the raw yearly numbers, not the model.
- **Data and code:** [this folder](https://github.com/kyledemes-pesonal/kyledemes-site/tree/main/data/2026-oa-backfile-citations) has the scripts, the aggregate results and a manifest that maps every number to its script.
