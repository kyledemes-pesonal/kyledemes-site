---
layout: post
title: "What if Canada had borrowed another country's open access policy?"
date: 2026-11-23 12:00:00 -0700
tags: [open-access, funding-data]
image: /data/2026-canada-oa-policy-designs/figures/2-canadian-copy-projections.png
image_alt: "Line chart: by 2030, the policy design decides whether 9% or 83% of tri-agency-funded papers have an open copy in Canada"
image_in_post: false
excerpt: "What if Canada had borrowed another country's open access policy? Under every design I sketched, the share of Canadian research that's free to read moves only a few points by 2030. Where funded papers live is another story: anywhere from 9% to 83% with an open copy in Canada."
---

*A follow-up to the open access monitor. Thinking out loud about what the new tri-agency policy might do, and what designs from other countries might have done instead.*

## The short version

When I built the monitor last week, the question in the back of my mind was simple: will the new tri-agency policy move Canada up the rankings? I kept following observations until I found myself asking: can we tell from other countries' approaches how much our policy will actually move the dial?

- **The share of all Canadian research that's free to read is mostly out of the policy's reach.** Only about a quarter of Canadian papers (26.5% to 30%) are tri-agency funded. Only grants awarded from 2027 are covered, and by 2030 those will be behind a third to a half of funded papers. And 74% to 82% of funded papers are already free to read, so there isn't much room left. Even if covered papers became as open as NIH- or UKRI-funded papers are today (90% to 95%), the share for all Canadian papers would rise only about 1 to 2 points by 2030, or about 3 if new grants turn into papers faster.
- **Elsewhere, the funder mandates that clearly pulled ahead had someone checking.** NIH-funded papers with a repository copy went from about half to 84% within two years of the 2008 US law. Canada's earlier policies had no routine checks, and they don't stand out against other countries or other funders.
- **Borrowing another country's design changes where papers live far more than how many are free.** In my rough sketches, every design leaves the middle estimate for all Canadian papers between about 74% and 79% free to read in 2030, and their ranges overlap. But the share of tri-agency-funded papers with an open copy in Canada ranges from about 9% (the policy as written, without grant-level checks) to about 83% (a US-style rule tied to grant payments that covers every new paper).
- **Which makes me wonder whether a tri-agency policy alone was ever going to do it.** Canada is 14th of 16 high-income countries on the share of its research that's free to read, and a rule that only reaches funded papers can't change that much.
- **I couldn't find the agencies' reasons for leaving the other designs out.** Most were asked for in the consultations. Why they were left out is the question I find most interesting, and I come back to it near the end.

## How far can the new policy move Canada's number?

My first instinct was that a policy covering all three of Canada's big research funders should be a big lever. Then I wrote down the multiplication.

**How I looked.** Three numbers multiply: the share of Canadian papers the agencies fund, how much room those papers have to become more open, and how many of them the policy reaches in a given year. I counted tri-agency papers in OpenAlex, checked how open they really are against random samples of Canadian papers whose funders I looked up in Crossref, and read award years off grant numbers to see how fast new grants turn into papers.

**What I found.**

- In 2025, 32,615 of the 122,884 papers with a Canadian author acknowledge CIHR, NSERC or SSHRC: 26.5%. OpenAlex can't see every funding acknowledgement, especially on closed papers, where it often has no full text to read. Allowing for the ones it misses, it's probably between 28% and 30%.
- Tri-agency-funded papers look more open than the rest of Canadian research (82% against 71%), but most of that gap is how funding gets detected. OpenAlex also finds funders in a paper's full text, which it mostly has for open papers (this is why it matters that funders ask publishers to share the raw acknowledgements text, not only structured funder metadata; [read more on that here](https://blog.openalex.org/who-funded-this-paper-lets-ask-the-authors/)). Counting only the funders publishers deposit in Crossref (which includes closed-access works as well), tri-agency-funded papers were 74% free to read in a 2024 sample and 78% in a 2025 sample, against 72% for all Canadian papers in both.
- A note on that 82%: the monitor showed 84% last week, counting every paper that acknowledges the agencies. Since then OpenAlex has linked about 2,000 more 2025 papers to the agencies, and only about 60% of those are open, so the same count is now 82.4%. Canadian-authored papers alone are 82.0%. The number will keep moving as funding data improves, and as repository harvesting does: as part of that work I did another systematic pass through Canadian repositories whose harvesting we could improve, and I'm fixing the handful that need it.
- The phase-in is slow. The policy applies to grants awarded from 1 January 2027, and papers acknowledge grants that are often several years old. Going by the award years inside NSERC, SSHRC and Canada Research Chairs grant numbers, new grants will be behind about 12% of funded papers published in 2028, 37% in 2030 and 85% in 2033. The gap between a grant and its papers has grown since 2019, maybe because of COVID extensions. If it goes back to what it was in 2020 to 2022, new grants would be behind about half of funded papers in 2030.
- Multiply it out and the ceiling for all Canadian papers by 2030 is +0.8 to +2.3 points (up to about +3.4 if the phase-in is faster), and +2 to +6 once the policy is fully phased in around 2034. All Canadian papers sit at 74.3% free to read, 43rd of the 55 countries with at least 20,000 papers. If every other country stood still, moving to 40th would take +1.7 points, and 30th +8.2. Even the top of the 2030 range moves Canada up only three places.

That was the first surprise, and it held up everywhere I looked: a funder rule lifts the papers it funds, and those are a minority everywhere. That alone may shock some people: national funders are behind a smaller share of their country's research than you might expect. NIH-funded papers are 95% free to read and the US as a whole is 70.5%. UKRI-funded papers are 97% and the UK is 84%. In 2025, every country I checked sat only 1 to 3 points above the share for papers its main funder didn't fund, and less once you allow for the funding OpenAlex can't see on closed papers. So where a country ranks seems to depend mostly on how open the rest of its research is, the papers its main funder didn't pay for, because that's most of it.

**Assumptions and caveats.** Free to read is measured today, not on publication day, so older years look more open than they were, and the most recent years look less open than they will. CIHR grant numbers don't carry a year, so I assumed CIHR papers follow the same lag as the others. The ceiling holds everything else still: Canada's funded papers are already getting more open through CRKN's read-and-publish deals, so the policy's own share of any gain will be smaller.

## What happened when other countries tried this?

If the national number barely moves, what about the policy's own goal? Comparing policies across countries is messy. Every country changed several things at once, counted things differently and started from a different place. Still, we can make some comparisons by looking at what other countries did and how far it moved the dial for them.

**How I looked.** For each policy, I took the open share the year before it started and four years after, in OpenAlex, and set that beside the median change for 15 other high-income countries over the same years (or, for a funder, beside other funders). Same yardstick for everyone, including Canada. It's a yardstick, not an experiment. In years with no policy at all, a country's change sits more than 6 points above or below the peer median about one time in four, so I only read the big gaps, and I check whether a country was already pulling ahead or falling behind before its policy started.

**What I found.**

| Policy (start) | Were individual grants checked? | What happened next |
| --- | --- | --- |
| US: NIH public access law (2008) | Yes: manuscript IDs in progress reports; from 2013, continuing awards delayed | NIH papers with a repository copy went from about half (2007) to 76% (2008) and 84% (2009), about 20 points more than other funders' papers gained |
| UK: Wellcome Trust sanctions (2012) | Yes: final grant payments withheld | Wellcome papers free to read went from 81% to 95%, closing 73% of the closed gap against 30% for other funders, mostly through paid open access in journals |
| UK: RCUK policy with publication-charge funding (2013), then the REF deposit rule (set 2014, in force 2016) | Yes, for the REF rule: papers that aren't open can't count in the national research assessment | UK free to read rose 28.7 points, against 12.9 for peers. About 60% of the extra came through repository copies and most of the rest through paid hybrid. Once the REF rule took effect, the UK didn't pull further ahead |
| Netherlands: right to share (2015), then universities depositing for authors (2021) | Universities deposit unless the author opts out | Dutch university papers open only through a repository went from 9% (2016) to 20% (2022). In OpenAlex the overall Dutch share, already near 90%, grew 4 points less than peers' over 2020 to 2025, while repository-only copies grew 5 points more |
| Finland, Sweden, Norway: national deals (from 2016) | Not a mandate: libraries paid publishers to open papers | Free to read rose 23 to 29 points over four years, against 14.7 for peers, almost all of it hybrid |
| Australia: NHMRC 12-month deposit (2012) | No | Funded papers rose 10 points, about 3 less than other funders' |
| Australia: ARC 12-month deposit (2013) | Not routinely | Funded papers rose 15.6 points, about 3 more than other funders', the one unchecked policy here that gained a little |
| Canada: CIHR policy (2008) | No | CIHR papers rose 7.8 points; other funders rose 13.3 |
| Canada: tri-agency harmonized policy (2015) | No routine checks | Canada rose 9.5 points, against 15.6 for peers, but it was already slipping about 3 points behind peers in each five-year stretch before 2015, and most of the extra gap came from other countries' publisher deals. NSERC- and SSHRC-funded papers each rose about 3 points less than other funders' |

Two things jumped out at me.

First, checking seems to matter most. The policies that clearly pulled ahead of their comparison group had money or eligibility attached, and someone looked. Some of them also paid for open access in journals at the same time (Wellcome and the UK research councils gained mostly through paid hybrid), so I can't fully separate checking from paying. The cleanest deposit-only case is the US: [a study with a stronger design](https://openalex.org/W3023725873) puts the NIH law's effect on free access to funded articles at about 50 points, and [compliance across funders](https://openalex.org/W2898324775) has been highest where funders enforce. NIH also made deposit easy: PubMed Central takes copies straight from many publishers. The ones without checks, including both of Canada's earlier policies, didn't stand out; Canadian and Australian authors kept publishing in journals that didn't fit their funders' policies ([a study of neuroscientists](https://openalex.org/W2899788429)). With this few cases, and so much else changing at the same time, I read that as a strong pattern rather than proof. The 2026 policy has the right instruments on paper (zero embargo, open licence, rights retention, a Canadian copy). The agencies say they will monitor compliance and report "in aggregate", and the FAQ treats not following an agency policy as a breach of the Responsible Conduct of Research framework, which is how individual cases would be handled. Their own 2024 consultation report says they weren't tracking compliance with the old policy. What I can't see yet is a routine check on individual grants, while other funders I work with have set up automated emails to grant PIs when they find papers they funded that don't comply with their policies.

Second, the fastest national jumps came from deals, not mandates. Canada has already done that through CRKN: hybrid open access went from 13% of tri-agency-funded papers in 2022 to 36% in 2025. That's about half of how Canada caught up with France in OpenAlex (74.3% and 74.4% in 2025), after trailing by 14 points in 2020. Most of the rest is a sharp drop in French papers that publishers make free without a licence, which may partly be a change in how they're recorded. This is interesting, and I'm going to follow up on how those deals (transformative agreements) actually changed publishing behaviour.

**Assumptions and caveats.** Comparing against peers isn't an experiment: other things change at the same time, and the UK's instruments arrived bundled together in 2012 to 2016. For funders, I counted every paper that acknowledges the funder, wherever its authors are. OpenAlex is still adding funder links to older papers, and most of the new ones are closed: between 22 and 23 November it linked 9% more 2014 papers to the agencies (a third more for SSHRC), which moved some funder rows by several points. I re-ran everything on 23 November, but treat funder comparisons before about 2017 as rough. The country rows don't depend on funder data. Later deposits lift the years before a policy more than the years after, so these comparisons, if anything, understate what the NIH law did. The Dutch 9% to 20% comes from the Dutch universities' own monitor; everything else in the table is OpenAlex.

## What if we'd borrowed someone else's design?

This is the picture I most wanted to see. I took four designs that worked somewhere else, imagined Canada had announced each one in October 2026 instead, and asked what each would do by 2030, next to the policy as written and the original 2025 draft.

![Line chart: the share of all Canadian papers free to read rose from 51% in 2016 to 74.3% in 2025. Projected to 2030, every policy design stays between about 74% and 79% (2026 policy without checks 74%, with checks 75%, 2025 draft 76%, US-style 77%, Netherlands-style 77%, France-style 77%, UK-style 79%), with overlapping ranges.](/data/2026-canada-oa-policy-designs/figures/1-free-to-read-projections.png)
<p class="figure-source">Source: OpenAlex API, pulled 22-23 Nov 2026 (2016 to 2025: published country table from the monitor). Projections: s5_projection_paths.py (version 2), results/projections.csv</p>

I know how awful it is to start a y-axis at 50% and end it at 80%, but the point here really is the subtle differences in a possible future tail, so please be kind. Even with the axis stretched, the lines stay close, and that surprised me more than anything else here. The ranges overlap so much that I can't really rank the designs on this measure. The ones that could do most reach beyond funded papers. A UK-style rule, where only deposited papers count when you apply for a grant, adds about 4 points by 2030 (77% to 80%), because most Canadian papers have at least one author who applies for tri-agency money. The 2026 policy with grant-level checks adds less than a point. The original 2025 draft would have added a little more, mostly because it would have started a year earlier. That's the funded-share arithmetic again: a funder rule can only move the papers it funds.

Nearly all of the big climb on the left came through journals: gold and hybrid together went from 18% of Canadian papers in 2016 to 53% in 2025, while papers open only through a repository went from 13% to 9%. The steepest part lines up with CRKN's read-and-publish deals.

## Where would the papers live?

Then I switched to the policy's own goal, an open copy of each funded paper in Canada, and the picture changed completely.

![Line chart: the share of tri-agency-funded Canadian papers with an open copy in a Canadian repository sat at 7% to 8% from 2016 to 2024 and 5.7% in 2025. Projected to 2030, the designs fan out: 2026 policy without checks 9%, with checks 25%, 2025 draft 34%, Netherlands-style 37%, France-style 48%, UK-style 53%, US-style 83%.](/data/2026-canada-oa-policy-designs/figures/2-canadian-copy-projections.png)
<p class="figure-source">Source: OpenAlex API, pulled 23 Nov 2026; open copies at the 99 Canadian repositories listed with the monitor (s1b_open_copies.py). Projections: s5_projection_paths.py (version 2), results/projections.csv</p>

Now the designs fan out. A US-style rule, with deposit as a condition of payment, gets about 83% of tri-agency-funded papers an open Canadian copy by 2030 (77% to 89%). Part of that is about which papers a rule reaches, not the payment condition: NIH's rule covered every paper accepted after it started, because Congress wrote it into law, while Canada's covers papers from grants awarded from 2027, the same way the 2015 policy started. With Canada's slower start, a US-style rule would reach about 35%. It also assumes something like PubMed Central, which publishers deposit into on authors' behalf. The 2026 policy gets about 25% with grant-level checks, and about 9% without them. The other designs land in between: the UK-style rule (about 53%), a French-style national archive (about 48%) and a Dutch-style right to share (about 37%, held back because it needs a law first).

The original 2025 draft is the line I keep looking at. Checked the same way, it gets about 34% of tri-agency-funded papers an open Canadian copy by 2030, against 25% for the final policy. Most of that gap is timing: had the draft been adopted on its own schedule, it would have covered grants awarded from 2026 rather than 2027. The rest comes from letting authors deposit a preprint when their publisher blocked the accepted manuscript, and that part is my own rough guess. The preprint route would matter most at the handful of big publishers that hold most closed tri-agency papers and don't allow immediate open-licence deposit without a fee.

The measured line caught my eye too. Counting only open copies, it sat at about 7% to 8% of funded papers from 2016 to 2024 and dips for 2025, which is mostly lag: deposits often arrive well after publication. Repository records, open or not, fell much more since 2019, and most of that is plumbing, not people: repositories whose old feed addresses went stale after a migration, and feeds reconnected this autumn that haven't fully reached OpenAlex yet. That's harvesting we're still catching up on. Whether authors deposit less once a paper is already open through a deal is still a fair question, but this line can't answer it yet.

## Should this have been a tri-agency policy at all?

Here's the thought I can't shake. The agencies can only set conditions on the grants they make, so their policy was always going to reach funded papers first. If the goal is to open up Canadian research as a whole, was a tri-agency policy ever going to be enough on its own, and whose job would the rest be?

Canada is 14th of 16 high-income countries on the share of all its research that's free to read (74.3% in 2025, level with France); other ways of counting put it between 12th and 15th, never out of the bottom five. Only the US (70.5%) and South Korea (59.3%) are lower, and the US also leans mostly on funder rules. Most of the countries near the top have something set nationally that covers all publicly funded research, not only papers from one funder's grants: a national target (Norway, Sweden, Finland, Switzerland), a national research assessment that only counts papers that are open (the UK), or a right to share plus universities depositing for authors (the Netherlands). But they share other things too: national deals with the big publishers, European funding rules, smaller research systems. With 16 countries I can't tell which of those matters most.

France is the interesting exception: a national plan since 2018, and level with Canada today. So a national policy isn't magic either. But I keep wondering what a Canadian approach would look like if it covered every paper from every Canadian institution, whoever paid for the research, and who would hold the pen in a country where universities answer to provinces. Switzerland is one answer: most of its universities are run by the cantons, and in 2017 its universities' association and national science funder wrote a national open access strategy together, at the federal government's request. Closer to home, Quebec's research funders have had their own immediate open access policy since 2022. I don't know what the Canadian version would be. It feels like a question worth asking out loud.

## So why didn't we go with these?

This is the question I keep coming back to, and what I'm trying to understand through these observations. The short answer is that I couldn't find it written down. The agencies' consultation reports list what people asked for. They don't say why each idea was taken up or left out. So this section is me reading the public record and trying hard not to fill the gaps with my own assumptions, but ultimately, these are guesses.

**What was asked for, on the record, and not adopted.**

- **A central repository like PubMed Central.** Many participants recommended one in the 2024 engagement, pointing to NIH's success, and it came up again in feedback on the 2025 draft.
- **Consequences tied to money.** Withholding funds from people who don't comply was suggested in both rounds, along with checking compliance in end-of-grant reports. CRKN asked for repository links in final reports and in future applications. The final policy mentions possible corrective actions affecting future eligibility, and the FAQ describes monitoring in aggregate.
- **Only open papers count.** Many participants in the 2024 engagement asked that only open access papers be considered when grant applications are reviewed, and CRKN proposed making past compliance a criterion when awarding grants. That's the closest Canada has come to the UK's REF rule, and [studies of deposit mandates](https://openalex.org/W1548026587) find that tying deposit to research evaluation is one of the conditions that goes with higher deposit.
- **A legal right to share.** Participants in both rounds asked the agencies to support a secondary publication right, and in 2024 some tied it to amending the Copyright Act.
- **A preprint for every paper, like the Gates Foundation's rule.** Since January 2025, the Gates Foundation has expected grantees to post a preprint of every funded paper unless there's a good reason not to, still requires the accepted article in an open repository under CC BY, and no longer pays publication charges. The February 2025 draft had a narrower version: a preprint under an open licence counted when a publisher wouldn't allow the accepted manuscript to be deposited. The final policy dropped it. (I suggested something along these lines in my own comments.)

**What the record does show about the constraints.**

- **Money, or how we make decisions?** It's tempting to say one central repository was too expensive. Canada had its own PubMed Central, and CIHR and the National Research Council took it offline in 2018, saying few researchers used it (about 4% of CIHR-funded manuscripts) and the upgrades it needed were too costly. But the model we chose isn't obviously cheaper. Most universities are on the hook to run and staff their own repository, many on the same shared software, and those without one lean on another library's "adoptive" repository. So far, the median Canadian university has a record of about 1.5% of its 2024-25 articles in its own repository, while Polytechnique Montréal records 98%, so it clearly can work. That makes me think this is less about money than about how we make decisions as a country: many institutions agreeing, rather than one body deciding. CARL's case for spreading it out (low cost, building on what libraries already run, no single point of failure if funding is cut) fits that instinct too. And no new money came with the policy: Budget 2026 has nothing for repositories, including CARL's request for $7 million over three years.
- **Copyright isn't the agencies' to change.** A Dutch-style right needs Parliament. The 2019 Commons review of the Copyright Act made no recommendation on it. (I should explore that idea for Canada in detail in another follow-up.)
- **Researchers' worries are long-standing.** In the 2013 consultation on the first tri-agency policy, about a third of researchers who responded said top journals weren't open access or didn't allow deposit.

**My current feeling.** These observations suggest the 2026 policy is a design that runs through libraries and consortia, costs the federal government little, and spreads the work across universities: CARL's repositories, CRKN's deals, Scholars Portal. CARL said plainly that a prescriptive policy would cost far less than one that defaults to paying publication charges. That's a coherent choice. It also leans on things the agencies don't control: whether every university can staff its repository, and whether the biggest publishers allow zero-embargo deposit. Canada has no national research assessment, universities answer to provinces, and the agencies' new CV asks for a handful of significant contributions rather than a full publication list. Any of those may be why a UK-style rule never got far, but I couldn't find anyone saying so. I expect to revise this as more data comes in, especially once we see who actually deposits in the first year or two.

**Maybe it was never mainly about the open share.** Maybe I've been looking at this too narrowly, assuming the goal was to raise the share of Canadian research that's open. Given how often CRKN and CARL appear in the record, and that the agencies name them as partners, it's entirely possible that some of the bigger motivations behind this policy had little to do with that number, and more to do with giving CRKN leverage in its negotiations with big publishers. The timing fits: CRKN's agreements with Elsevier, Sage and Wiley end on 31 December 2026, the day before the policy starts. The agency presidents co-signed CRKN's April 2026 statement backing its negotiation principles, and their letter to publishers points to that signature. The preprint option was dropped after CRKN told the agencies it undermined the leverage rights retention gives CRKN in negotiations (it also worried about unreviewed papers in repositories), and CARL and other respondents said it weakened the policy too. There's evidence the other way as well: the review started in July 2023, before CRKN's 2026 principles existed, and publication charges are still an eligible grant cost. Apart from that one line in the letter, the agencies' texts talk about access, cost and sovereignty, not negotiations, so I can't say how much weight each had. But if leverage was a big part of it, the open share was never the right yardstick, and the 2027 renewals are. I'll be watching those.

That would make sense, given how much of the conversation in Canada has been about five big publishers as an oligopoly. I went in expecting those five to look much smaller in an inclusive database like OpenAlex, and that turned out to be only half right. Worldwide they do: Elsevier, Springer Nature, Wiley, Taylor & Francis and Sage published about 40% of 2025 journal articles with a known publisher in OpenAlex, against well over half in studies built on Web of Science ([a 2025 study comparing the databases](https://openalex.org/W4400104364)). But Canadian research leans on them more than the world does: about 55% of Canadian-authored articles. So there's no arguing they aren't among the most important publishers for Canadian researchers. What I'm less sure about is whether negotiating with them should be such a big part of what drives an open access policy. And I wonder what all of this means for a publisher like Canadian Science Publishing, a small Canadian nonprofit that publishes under 1% of Canadian-authored articles and will feel this policy too. That's one I want to follow up on soon.

## What none of this can tell us

- **Whether, and how, the agencies will check individual grants.** Almost everything in the projections turns on that, and it hasn't been decided in public. It's incredibly simple to set up automations that check compliance and provide support to the people doing the deposits, and some funders are already doing that.
- **How the biggest publishers will answer.** On 18 November, none of the five publishers holding most closed tri-agency papers let authors put the accepted manuscript in an institutional repository immediately, under an open licence, at no charge (Taylor & Francis does for a few dozen library-science journals, and ACS does for a US$2,500 fee).
- **What a "trusted Canadian platform" will mean.** If Scholars Portal Journals counts broadly, much of today's gold and hybrid output could count with no new deposit, and the Canadian-copy number would jump on paper overnight.
- **The future.** The projections are rough sketches, not forecasts or targets for the agencies. They borrow effects from other countries, other decades and other research systems, and they hold everything else still. Because open access keeps growing on its own, the real 2030 numbers will be higher than every line here. If you quote one, please quote its range and what it assumes.
- **Why any design was chosen.** Only the agencies' own decision records could settle that. Everything in the last section about reasons is either a quoted request or my current feeling.

## How I did it

- **Data.** OpenAlex API, pulled 22 and 23 November 2026. Articles and reviews. Two groups throughout: all Canadian papers (at least one author with a Canadian affiliation) and tri-agency-funded papers (Canadian papers that acknowledge CIHR, NSERC or SSHRC, using the same 12 OpenAlex funder records as the monitor; the monitor also counted funded papers with no Canadian author, which changes the open share by less than half a point). Free to read means OpenAlex doesn't mark the paper closed today: any version, any licence, including about 5% of Canadian papers whose only free copy is a preprint or other submitted version, and copies that appeared years after publication. That's a looser yardstick than the policy, which asks for no embargo, an open licence and a Canadian copy. A Canadian copy here means an open copy in one of the 99 Canadian repositories listed with the monitor (between half and two-thirds of the papers those repositories hold a record of have an open copy there, depending on the year).
- **How open funded papers really are.** Random samples of about 1,600 Canadian papers with DOIs for 2024 and 2025, each looked up in Crossref, comparing the funders publishers deposited with the funders OpenAlex found.
- **Phase-in.** For each publication year from 2017 to 2025, 1,000 random Canadian papers with an NSERC, SSHRC or Canada Research Chairs grant number; the award year read from the number (about 60% of sampled papers in 2023 to 2025 had a number I could read a year from; the rest look similar where a year is visible); the gap between award and paper, using 2023 to 2025 papers, to estimate how many funded papers new grants will cover each year.
- **Other countries.** Open share the year before each policy and four years after, against the median change of 15 other high-income countries (or of other funders) over the same years, with a check of the years before each policy. Re-run on 23 November after OpenAlex added funder links to older papers.
- **Projections.** One rule for every design: the gain over peers that a similar policy got elsewhere (the share of closed papers it opened beyond what its comparison group opened), applied to Canada's own closed papers, then spread over time by how fast the design would reach papers. Everything other than the design is held at its 2025 level. Each range pairs my most cautious assumptions with my most generous ones, so the dot in the middle isn't a best guess. The table below gives what each line assumes.

| Design | Which papers it reaches, and when | What it does to them | Based on |
| --- | --- | --- | --- |
| 2026 policy, without grant-level checks | Tri-agency-funded papers from grants awarded from 2027: 37% of them in 2030 | 0 to 2 points more open; 9% to 17% with an open Canadian copy | Canada 2015, CIHR 2008, NHMRC 2012 |
| 2026 policy, with grant-level checks | Same as above | Opens 17% to 43% of those papers' closed gap; 45% to 65% with an open Canadian copy | FWF, Horizon 2020 and Wellcome against other funders; REF first-year compliance |
| 2025 draft, with grant-level checks | Tri-agency-funded papers from grants awarded from 2026: 53% of them in 2030 | As above, plus a small bump for the preprint route (my guess); 48% to 70% with an open Canadian copy | The February 2025 draft. OpenAlex counts a preprint toward the published paper only when it links the two |
| US-style: deposit a condition of payment | Every funded paper accepted from 2027, compliance building over two years as NIH's did | Opens about half of those papers' closed gap; 77% to 89% with an open Canadian copy | NIH 2008 against other funders; assumes a national service that takes copies straight from publishers, as PubMed Central does |
| UK-style: only deposited papers count when you apply | Every paper applicants list, funded or not: about 60% to 80% of Canadian output (in a random sample of 600 Canadian 2024 papers, 65% to 72% had a Canadian author with at least three to five tri-agency-funded papers since 2019), arriving with the announcement, in full by 2030 | Opens 17% to 30% of those papers' closed gap (the UK's gain over peers, without and with the paid hybrid that came with it); 40% to 65% of funded papers with an open Canadian copy | RCUK and REF, 2013 to 2017 |
| Netherlands-style: a right to share, universities deposit | Needs a Copyright Act change (assumed in force 2028); universities producing 25% to 50% of output depositing by 2030 | Opens up to about 40% of their papers' closed gap (the Dutch gain over peers in repository-only copies); 75% to 95% of their papers with an open Canadian copy | Netherlands, 2020 to 2025 |
| France-style: one national archive as the publication record | Grant reports and university records drawn from repositories, building over four years | +1 to +4 points for all Canadian papers by 2030; 35% to 60% of funded papers with an open Canadian copy | France 2018, ANR |

**Data and code:** [github.com/kyledemes-pesonal/kyledemes-site/tree/main/data/2026-canada-oa-policy-designs](https://github.com/kyledemes-pesonal/kyledemes-site/tree/main/data/2026-canada-oa-policy-designs) (scripts, aggregate results and both charts' rows).

## Sources

Canadian policy record

- [Tri-Agency Open Access Policy on Publications (2026)](https://science.gc.ca/site/science/en/interagency-research-funding/policies-and-guidelines/open-access/tri-agency-open-access-policy-publications-2026)
- [Draft revised policy (February 2025)](https://science.gc.ca/site/science/en/node/1350)
- [Guidance and FAQ for the 2026 policy](https://science.gc.ca/site/science/en/interagency-research-funding/policies-and-guidelines/open-access/guidance-and-frequently-asked-questions-2026-tri-agency-open-access-policy-publications)
- [Letter to Publishers (October 2026)](https://science.gc.ca/site/science/en/interagency-research-funding/policies-and-guidelines/open-access/letter-publishers)
- [What We Heard: engagements on the review of the policy (2024)](https://science.gc.ca/site/science/en/interagency-research-funding/policies-and-guidelines/open-access/what-we-heard-report-engagements-review-tri-agency-open-access-policy-publications-2024)
- [Summary of feedback on the draft revised policy (2025)](https://science.gc.ca/site/science/en/interagency-research-funding/policies-and-guidelines/open-access/summary-feedback-draft-revised-tri-agency-open-access-policy-publications-2025)
- [Summary of responses to the 2013 draft policy (2014)](https://web.archive.org/web/2017/http://www.nserc-crsng.gc.ca/_doc/NSERC-CRSNG/NSERC-SSHRC-OpenAccess_e.pdf)
- [CIHR: PubMed Central Canada taken offline (2018)](https://cihr-irsc.gc.ca/e/50728.html)
- [Budget 2026](https://budget.canada.ca/2026/report-rapport/toc-tdm-en.html)
- [House of Commons INDU, Statutory Review of the Copyright Act (2019)](https://www.ourcommons.ca/Content/Committee/421/INDU/Reports/RP10537003/indurp16/indurp16-e.pdf)
- [Fonds de recherche du Québec, open access policy (2022)](https://www.frq.gouv.qc.ca/app/uploads/2022/10/open_access_dissemination_policy_vf.pdf)

Libraries and consortia

- [CARL, comments on the draft policy (March 2025)](https://www.carl-abrc.ca/wp-content/uploads/2025/05/Talking-Points-Tri-Agency-OA-Policy.pdf)
- [CARL, Budget 2026 brief (May 2026)](https://www.carl-abrc.ca/wp-content/uploads/2026/06/CARL_Budget_2026_brief.pdf)
- [CRKN, response to the draft policy (May 2025)](https://www.crkn-rcdr.ca/en/crkns-response-tri-agency-draft-open-access-policy)
- [CRKN, research community alignment on the 2026 licence negotiations (April 2026)](https://www.crkn-rcdr.ca/en/canadian-research-community-alignment-crkns-2026-license-negotiations)

Other countries

- [NIH, revised public access policy notice NOT-OD-08-033 (January 2008)](https://webarchive.library.unt.edu/eot2008/20090507014524mp_/http:/grants.nih.gov/grants/guide/notice-files/NOT-OD-08-033.html)
- [Wellcome Trust strengthens its open access policy (June 2012)](https://wellcome.org/press-release/wellcome-trust-strengthens-its-open-access-policy)
- [Gates Foundation open access policy (from January 2025)](https://openaccess.gatesfoundation.org/open-access-policy/)
- [Universities of the Netherlands, letter on the 2022 open access monitor (September 2023)](https://www.universiteitenvannederland.nl/files/publications/UNL%2023048%20U%20-%20OCW%20-%20%20Monitor%20Open%20Access%202022%20en%20vervolg_0_0.pdf)
- [Swiss National Science Foundation: Swiss open access strategy approved (2017)](https://www.snf.ch/en/6T8e575h4pa9UaKo/news/news-170201-swiss-open-access-strategy-approved)

Studies

- [The Impact of Open Access Mandates on Invention](https://openalex.org/W3023725873)
- [Do authors comply when funders enforce open access to research?](https://openalex.org/W2898324775)
- [A Very Long Embargo: Journal Choice Reveals Active Non-Compliance with Funder Open Access Policies by Australian and Canadian Neuroscientists](https://openalex.org/W2899788429)
- [Estimating open access mandate effectiveness: The MELIBEA score](https://openalex.org/W1548026587)
- [Scholarly publishing's hidden diversity: how exclusive databases sustain the oligopoly of academic publishers](https://openalex.org/W4400104364)

Funding data

- [OpenAlex blog: Who funded this paper? Let's ask the authors (November 2026)](https://blog.openalex.org/who-funded-this-paper-lets-ask-the-authors/)

Earlier field note

- [Where Canada's open research lives](https://kyledemes.com/notes/2026/where-canadas-open-research-lives/) (the monitor, its repository list and country table)
