# kyledemes.com

Personal site, built by GitHub Pages (Jekyll). To add a post, add a markdown file to `_posts/` named `YYYY-MM-DD-slug.md` with front matter (`layout: post`, `title`, `date`) and push to `main`. Images go in `assets/img/`.

Every post needs a photo or a figure (Kyle, 19 Nov 2026, modelled on aarondemes.com). Set `image:` (and `image_alt:`) in the front matter: it becomes the post's card on the Field notes page, its thumbnail in the homepage list, its social-share image, and a figure at the top of the post. Use `image_in_post: false` when the post already opens with its own figure, `image_position:` to steer the crop, and `excerpt:` for the card text if the first paragraph doesn't work.

## Posts that use OpenAlex data

Each one gets a folder `data/<year>-<slug>/` with a README (browser-checkable API links for the headline numbers, run order), `scripts/` (Python, standard library + matplotlib), and `results/` (the CSV behind every figure). The post links to its folder.

## Email sign-ups

The "Get new field notes by email" box (`_includes/subscribe.html`, shown on the homepage, the Field notes page and every post) submits to the Google Form "Field notes sign-ups" in kyle@demes.ca's Drive. Each sign-up lands as a row (timestamp, email) in the Google Sheet "Field notes subscribers". The form ID and field (`entry.1045046103`) are in the include. To move to a newsletter service later, export the Sheet as CSV and import it there.

## Tags

Posts list themes by slug in the front matter (`tags: [open-access, funding-data]`). Each tag needs two things: an entry in `_data/tags.yml` (display name and one-line description) and a stub page at `notes/tags/<slug>/index.html` (copy an existing stub, change `tag:` and `title:`). GitHub Pages runs no tag plugin, so a tag without its stub has no page. `notes/tags/` lists every tag.
