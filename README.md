# kyledemes.com

Personal site, built by GitHub Pages (Jekyll). To add a post, add a markdown file to `_posts/` named `YYYY-MM-DD-slug.md` with front matter (`layout: post`, `title`, `date`) and push to `main`. Images go in `assets/img/`.

## Posts that use OpenAlex data

Each one gets a folder `data/<year>-<slug>/` with a README (browser-checkable API links for the headline numbers, run order), `scripts/` (Python, standard library + matplotlib), and `results/` (the CSV behind every figure). The post links to its folder.

## Email sign-ups

The "Get new field notes by email" box (`_includes/subscribe.html`, shown on the homepage, the Field notes page and every post) submits to the Google Form "Field notes sign-ups" in kyle@demes.ca's Drive. Each sign-up lands as a row (timestamp, email) in the Google Sheet "Field notes subscribers". The form ID and field (`entry.1045046103`) are in the include. To move to a newsletter service later, export the Sheet as CSV and import it there.
