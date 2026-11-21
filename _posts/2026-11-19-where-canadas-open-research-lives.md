---
layout: post
title: "Where Canada's open research lives"
date: 2026-11-19 10:00:00 -0800
tags: [open-access, funding-data]
image: /data/2026-where-canadas-open-research-lives/figure.png
image_alt: "Line chart: 84% of 2025 tri-agency papers are free to read, but 8% have a copy in a Canadian repository"
image_in_post: false
excerpt: "Most of Canada's publicly funded research is already free to read. Almost none of it lives where the new tri-agency open access policy will ask. A small monitor to see where we're starting from."
---

*A small monitor for the tri-agency open access policy.*

On 1 January, Canada's three research funding agencies start a new open access policy. Papers from grants awarded from that date have to be free to read the day they're published, under an open licence, with a copy in a Canadian repository or on a trusted Canadian platform. I'm not reflecting on the policy itself here (in fact, I gave my comments to the tri-agencies during their consultation). But I wanted to know where we're starting from, so I built a small monitor to start thinking about these things.

<iframe id="oa-monitor" class="oa-embed" src="{{ '/data/2026-where-canadas-open-research-lives/monitor.html' | relative_url }}" title="Canadian Open Access Monitor" style="width:100%;min-height:900px;border:0;display:block" loading="lazy"></iframe>
<script>
window.addEventListener('message', function (e) {
  if (!e.data || !/^oa-[a-z]+-height$/.test(e.data.type)) return;
  document.querySelectorAll('iframe.oa-embed').forEach(function (f) { if (f.contentWindow === e.source) f.style.height = e.data.h + 'px'; });
});
</script>

<p class="meta"><a href="{{ '/data/2026-where-canadas-open-research-lives/monitor.html' | relative_url }}">Open the monitor on its own page</a></p>

A few things stood out.

**Most Canadian research is already free to read.** 84% of 2025 papers that acknowledge CIHR, NSERC or SSHRC are free to read somewhere today, and 74% of all Canadian research is.

**Almost none of it lives where the policy will ask.** About 8% of those papers have a copy in a Canadian repository that OpenAlex can see. That number is only as good as the harvesting behind it, so we've been working on it. Canada has taken a hybrid approach to repositories: many universities run the same software through Scholaris, the shared service from Scholars Portal, but each runs its own instance, and when a repository moves, its harvest address changes. In September, ahead of a talk to the Scholaris community, we audited all 26 live Scholaris repositories and found OpenAlex was harvesting only 2 of them, because most had migrated and we were still reading their old addresses. Today all 26 are harvested, about 595,000 records, and in a test set of 392 known deposits the number we could find went from 195 to 242. An independent study found the same picture at the U15, where a mean of 4.2% of papers sit in the authors' own repositories. The distance from 8% to what the policy asks is where the work is.

The share with a Canadian repository copy has also fallen since 2019. Some of that is lag, since deposits often come well after publication, and some is harvesting we're still fixing. But some may be authors no longer depositing papers that are already open through read-and-publish deals. If that holds up, it's a finding in its own right, and I'll come back to it.

**The way papers become open has changed.** Hybrid open access went from 14% of tri-agency papers in 2022 to 36% in 2025, in step with CRKN's read-and-publish agreements. At list price, the tri-agency gold and hybrid papers published in 2025 carry about US$72 million in article processing charges. That isn't what Canada paid, since agreements cover much of it, but it's the scale of what's being bought. For comparison, Leigh-Ann Butler, Stefanie Haustein and colleagues used the same approach for 2015 to 2018 and found US$27.6 million over the four years at the five largest publishers alone. On that same scope OpenAlex finds nearly the same set of papers, so the growth is real: more papers, more of them hybrid, and higher prices.

**Diamond is bigger than it looks for funded research.** Diamond open access (free to read and free to publish) is 9% of all Canadian research but only 4% of tri-agency papers. Part of that is real: diamond in Canada is concentrated in the humanities and social sciences and in clinical, professional, government and student journals, where grants are less common. Part of it is measurement: diamond journals rarely record funders in their metadata. Only 13% of Canadian diamond papers list any funder in Crossref, against 55% to 59% of gold and hybrid papers, so funded diamond papers are undercounted, especially for SSHRC. The new grant-number requirement should help them show up.

**Grant numbers are the quiet win.** The policy requires every paper to name its grant. Today 58% of CIHR papers, 53% of NSERC papers and 53% of SSHRC papers carry their agency's grant number, up from 30% overall in 2015. I expect this to be the first thing that visibly changes.

**The closed papers sit at a handful of publishers.** About 5,400 tri-agency papers from 2025 have no free copy, and most are at Elsevier, Springer Nature, ACS, Taylor & Francis and IEEE. Going by their public policies on 18 November, none of those five lets authors share the accepted manuscript immediately, free, under an open licence (Taylor & Francis does for a few dozen library-science journals). Canadian Science Publishing, Sage and Cambridge do. How those publishers answer the agencies' letter will shape how this policy plays out.

### How this compares with the agencies' numbers

The agencies published two baselines in October:

- 68.6% of Canadian-authored articles open in 2025;
- 73.0% of NSERC-funded, 72.4% of SSHRC-funded and 85.3% of CIHR-funded articles.

The monitor's figures run higher. For Canada as a whole, most of the gap closes if you leave out "bronze" papers, which are free on a publisher's site but carry no licence: that gives 70.4%, against their 68.6%. For funded papers, the rest likely comes from how funding is detected. The agencies say they'll track their numbers using open data sources, and OpenAlex is one, so I'd expect the figures to line up as the methods are compared. Both measure papers that are free to read anywhere, which isn't the same as meeting the new policy. The gap between those two things is the story.

### How Canada compares

Two more charts put those numbers in context: every Canadian university, and every country. In the first, pick the U15 or a province to bring their universities forward, or compare up to five universities by name. In the second, pick any country.

<iframe class="oa-embed" src="{{ '/data/2026-where-canadas-open-research-lives/trends.html' | relative_url }}" title="Open access over time: Canadian universities and countries" style="width:100%;min-height:1100px;border:0;display:block" loading="lazy"></iframe>

<p class="meta"><a href="{{ '/data/2026-where-canadas-open-research-lives/trends.html' | relative_url }}">Open the charts on their own page</a></p>

**Canadian universities move together.** In 2010, between 22% and 48% of each university's papers were free to read (counting universities with at least 200 papers that year). In 2025 it was between 67% and 82%, and the U15 sat between 72% and 79%. The lines rise as a bundle, and the bundle has tightened. Provinces tell the same story: Quebec and British Columbia led for most of the decade, and by 2025 every province is within about six points of the others.

**Canada lost ground in the 2010s and has mostly made it back.** In 2010, Canada was a little ahead of the world, 39% free to read against 36%. Through the 2010s much of Europe moved faster, and by 2020 Canada was seven points behind the world. The gap closed in 2023 and 2024, the years of CRKN's largest read-and-publish agreements: hybrid open access rose 7 points in Canada in 2024, against 3 points in the United States. Canada is now two points behind the world (74% against 76%). Among the 55 countries with at least 20,000 papers in 2025, that puts Canada 43rd, behind most of Europe, Latin America and Australia, level with France and Japan, and ahead of the United States and China.

**2026 is a partial year.** It covers papers published so far, and the most recent years always look a little low, because repository copies often arrive months after publication.

I also tried to assess whether individual universities' own open access policies and author funds made a difference. None showed a clear signal against the national trend, so I've left that aside for now. The sourced timeline of university policies, funds and national agreements is in the [data folder](https://github.com/kyledemes-pesonal/kyledemes-site/tree/main/data/2026-where-canadas-open-research-lives/results) for anyone who wants to take it further.

### What this isn't

It isn't a compliance report. Papers published so far come from grants under the 2015 rules, and papers from 2027 grants won't show up in numbers until 2028. Think of it as the starting line.

It doesn't rank universities. The chart shows every university so you can find your own, but the differences between them are small and depend partly on how well each repository is harvested.

It isn't official. I built it myself on open data from OpenAlex, and I should be clear about where I sit: I'm the COO of OpenAlex, and I'm on the board of Canadian Science Publishing, which appears in one chart. The [scripts and data](https://github.com/kyledemes-pesonal/kyledemes-site/tree/main/data/2026-where-canadas-open-research-lives) are open, so anyone can check the numbers or run them differently.

### Why build it at all

France has run a national open science barometer since 2018, with open code. Japan copied that code this year and runs it on OpenAlex, and Germany and Switzerland run their monitors on OpenAlex too. Canada has two headline numbers and no tool. I'd like that to change, and the quickest way to start the conversation was to build a rough version and put it in front of people.

I'm not trying to own this. The right long-term home is Canadian: a library consortium, a university group or the agencies themselves. If that's you, I'd love to talk.

And if you spot a wrong number, tell me at kyle@demes.ca. I'll check it and fix it.
