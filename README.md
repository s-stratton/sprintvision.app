# SprintVision Landing Page (static)

This repo contains a static landing page scaffold for SprintVision (a sprint analysis app).

To view locally:

1. Open `index.html` in your browser, or
2. Run a local server from the project root, for example:

```bash
python3 -m http.server 8000
# then open http://localhost:8000 in your browser
```

Files created:
- `index.html` — landing page markup
- `css/styles.css` — theme and responsive styles
- `assets/` — placeholder SVGs for logo and screenshots
- `assets/` — placeholder assets. Place your PNG logo at `assets/sprint_vision_logo.png` (file name expected by the markup).

## Blog

Posts live in `_blog/posts/*.html`: a JSON header in an HTML comment (title, description, date, image, summary, FAQ, related posts), then the article body. After adding or editing a post, run:

```bash
python3 _blog/build.py
```

This regenerates `blog/` (every post and the index), `sitemap.xml` and `llms.txt`. Edit the files in `_blog/`, not the generated HTML. Jekyll skips `_blog/`, so it isn't published.
