---
layout: default
title: Career
permalink: /about/
---

# Career

My work has touched nearly every part of the research system: doing research, supporting researchers, advising institutions and governments, and now running open research infrastructure.

<div class="tl">
{% for c in site.data.career %}
  <div class="item{% if c.past %} past{% endif %}"><div class="when">{{ c.when }}</div><div class="what">{{ c.what }}</div><div class="where">{{ c.where }}</div><p>{{ c.text }}</p></div>
{% endfor %}
</div>

Also: BS Biology (cum laude), University of South Florida.
