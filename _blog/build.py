#!/usr/bin/env python3
"""Builds the blog from _blog/posts/*.html.

Each post file starts with a JSON header in an HTML comment, then the
article body. Run `python3 _blog/build.py` from anywhere; it writes
blog/<slug>/index.html, blog/index.html, sitemap.xml and llms.txt.
Jekyll skips folders starting with "_", so this one isn't published.
"""
import html
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTS = ROOT / "_blog" / "posts"
SITE = "https://sprintvision.app"
STORE = "https://apps.apple.com/ie/app/sprintvision-sprint-analysis/id6782655591"
FONTS = "https://fonts.googleapis.com/css2?family=Mona+Sans:ital,wdth,wght@0,75..125,200..900;1,75..125,200..900&display=swap"

# Pages outside the blog, for the sitemap.
PAGES = [("", "1.0"), ("contact.html", "0.3"), ("privacy.html", "0.2"), ("terms.html", "0.2")]


def esc(s):
    return html.escape(s, quote=True)


def load_posts():
    posts = []
    for f in sorted(POSTS.glob("*.html")):
        text = f.read_text()
        m = re.match(r"\s*<!--(.*?)-->\s*(.*)", text, re.S)
        meta = json.loads(m.group(1))
        meta["body"] = m.group(2).strip()
        words = len(re.sub(r"<[^>]+>", " ", meta["body"]).split())
        meta["minutes"] = max(1, round(words / 230))
        posts.append(meta)
    # Newest first; ties keep the "order" field.
    posts.sort(key=lambda p: (p["date"], -p.get("order", 0)), reverse=True)
    return posts


def nice_date(d):
    return date.fromisoformat(d).strftime("%-d %B %Y")


def head(title, description, url, image, up, og_type="website", extra=""):
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <link rel="canonical" href="{url}">
  <link rel="icon" type="image/png" sizes="32x32" href="{up}assets/favicon-32.png">
  <link rel="apple-touch-icon" sizes="180x180" href="{up}assets/apple-touch-icon.png">
  <meta name="theme-color" content="#ffffff">
  <meta property="og:type" content="{og_type}">
  <meta property="og:site_name" content="SprintVision">
  <meta property="og:url" content="{url}">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:image" content="{SITE}/{image}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(description)}">
  <meta name="twitter:image" content="{SITE}/{image}">
  <link rel="alternate" type="text/plain" title="SprintVision for AI assistants" href="{SITE}/llms.txt">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="{FONTS}" rel="stylesheet">
  <link rel="stylesheet" href="{up}css/styles.css">
  <script>document.documentElement.classList.add('js');</script>
{extra}</head>"""


def header(up):
    return f"""  <header class="top">
    <div class="wrap top-inner">
      <a href="{up}index.html" class="brand"><img src="{up}assets/sprint_vision_logo.png" alt="" width="32" height="32"><span>SprintVision</span></a>
      <nav class="top-nav" aria-label="Main">
        <a href="{up}index.html#how">How it works</a>
        <a href="{up}index.html#steps">Every step</a>
        <a href="{up}index.html#fix">What to fix</a>
        <a href="{up}index.html#filming">Filming</a>
        <a href="{up}blog/" aria-current="page">Blog</a>
      </nav>
      <a class="btn btn-ink" href="{STORE}" target="_blank" rel="noopener">Get the app</a>
    </div>
  </header>"""


def footer(up):
    return f"""  <footer class="foot">
    <div class="wrap">
      <div class="foot-top">
        <div class="foot-brand">
          <a href="{up}index.html" class="brand"><img src="{up}assets/sprint_vision_logo.png" alt="" width="32" height="32"><span>SprintVision</span></a>
          <p>Stop guessing. Start getting faster.</p>
          <a class="store" href="{STORE}" target="_blank" rel="noopener"><img src="{up}assets/Download_On_AppStore.svg" alt="Download on the App Store" width="135" height="45" loading="lazy"></a>
        </div>
        <nav class="foot-col" aria-label="Product">
          <h4>Product</h4>
          <a href="{up}index.html#how">How it works</a>
          <a href="{up}index.html#steps">Every step</a>
          <a href="{up}index.html#fix">What to fix</a>
          <a href="{up}index.html#filming">Filming tips</a>
          <a href="{up}blog/">Blog</a>
        </nav>
        <nav class="foot-col" aria-label="Company">
          <h4>Company</h4>
          <a href="{up}contact.html">Contact us</a>
          <a href="{up}privacy.html">Privacy policy</a>
          <a href="{up}terms.html">Terms of use</a>
        </nav>
        <nav class="foot-col" aria-label="Follow">
          <h4>Follow</h4>
          <a href="https://vm.tiktok.com/ZNRoRgNN7/" target="_blank" rel="noopener">TikTok</a>
          <a href="https://www.instagram.com/sprintvisionapp" target="_blank" rel="noopener">Instagram</a>
          <a href="https://x.com/sprintvisionapp" target="_blank" rel="noopener">X</a>
        </nav>
      </div>
      <p class="foot-legal">© 2026 SprintVision. All rights reserved.</p>
    </div>
  </footer>

  <div class="sticky" data-sticky>
    <img src="{up}assets/sprint_vision_logo.png" alt="" width="36" height="36">
    <span class="sticky-text"><b>SprintVision</b><span>Free trial · iPhone</span></span>
    <a href="{STORE}" target="_blank" rel="noopener">Get the app</a>
  </div>

  <script src="{up}js/site.js" defer></script>
  <!-- Cloudflare Web Analytics --><script type='module' src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{{"token": "57adea9f038b44659b6eff30df797184"}}'></script><!-- End Cloudflare Web Analytics -->
</body>
</html>
"""


def focus(p):
    """Where to centre the crop when a photo is shown cropped."""
    pos = p.get("image_pos")
    return f' style="object-position:{pos}"' if pos else ""


def ld(obj):
    return ('  <script type="application/ld+json">\n'
            + json.dumps(obj, ensure_ascii=False, indent=2) + "\n  </script>\n")


PUBLISHER = {
    "@type": "Organization",
    "name": "SprintVision",
    "url": SITE + "/",
    "logo": {"@type": "ImageObject", "url": SITE + "/assets/sprint_vision_logo.png"},
}


def post_page(p, posts):
    up = "../../"
    url = f"{SITE}/blog/{p['slug']}/"
    schema = [{
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": p["title"],
        "description": p["description"],
        "image": f"{SITE}/{p['image']}",
        "datePublished": p["date"],
        "dateModified": p.get("updated", p["date"]),
        "author": PUBLISHER,
        "publisher": PUBLISHER,
        "mainEntityOfPage": url,
        "about": p.get("about", []),
        "inLanguage": "en",
    }, {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": SITE + "/blog/"},
            {"@type": "ListItem", "position": 3, "name": p["title"], "item": url},
        ],
    }]
    if p.get("app_schema"):
        # Posts about the app itself also describe it as an app, so search
        # and AI answers can connect the page to SprintVision.
        schema.append({
            "@context": "https://schema.org",
            "@type": "MobileApplication",
            "name": "SprintVision: Sprint Analysis",
            "operatingSystem": "iOS",
            "applicationCategory": "SportsApplication",
            "description": p["app_schema"],
            "downloadUrl": STORE,
            "image": f"{SITE}/assets/og-image.jpg",
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
            "publisher": PUBLISHER,
        })
    if p.get("faq"):
        schema.append({
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [{
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            } for q, a in p["faq"]],
        })
    extra = "".join(ld(s) for s in schema)

    summary = "\n".join(f"          <li>{s}</li>" for s in p["summary"])
    faq = ""
    if p.get("faq"):
        items = "\n".join(
            f"        <details>\n          <summary>{esc(q)}</summary>\n          <p>{esc(a)}</p>\n        </details>"
            for q, a in p["faq"])
        faq = f"""
      <section class="post-faq" aria-labelledby="faq">
        <h2 id="faq">Common questions</h2>
{items}
      </section>"""

    related = [r for r in posts if r["slug"] in p.get("related", [])][:3]
    related_html = "\n".join(card(r, up, "h3") for r in related)

    updated = ""
    if p.get("updated") and p["updated"] != p["date"]:
        updated = f' · Updated <time datetime="{p["updated"]}">{nice_date(p["updated"])}</time>'

    return f"""{head(p['title'] + ' — SprintVision', p['description'], url, p['image'], up, 'article', extra)}
<body class="blog">
{header(up)}

  <main>
    <article class="post">
      <header class="wrap post-head">
        <nav class="crumbs" aria-label="Breadcrumb"><a href="{up}blog/">Blog</a><span aria-hidden="true">/</span><span>{esc(p['kicker'])}</span></nav>
        <h1>{esc(p['title'])}</h1>
        <p class="post-dek">{esc(p['dek'])}</p>
        <p class="post-meta">By SprintVision · <time datetime="{p['date']}">{nice_date(p['date'])}</time>{updated} · {p['minutes']} min read</p>
      </header>

      <div class="wrap post-wrap">
        <figure class="post-hero">
          <img src="{up}{p['image']}" alt="{esc(p['image_alt'])}" width="{p['image_w']}" height="{p['image_h']}"{focus(p)}>
          <figcaption>{p['caption']}</figcaption>
        </figure>

        <aside class="tldr" aria-label="Key points">
          <p class="label">In short</p>
          <ul>
{summary}
          </ul>
        </aside>

        <div class="prose">
{p['body']}
        </div>
{faq}

        <section class="post-cta">
          <div>
            <h2>See your own numbers.</h2>
            <p>Film one rep on your iPhone. SprintVision measures every step and rates your positions against these targets, with a cue for anything outside the range.</p>
          </div>
          <div class="cta">
            <a class="store" href="{STORE}" target="_blank" rel="noopener"><img src="{up}assets/Download_On_AppStore.svg" alt="Download on the App Store" width="150" height="50" loading="lazy"></a>
            <span class="cta-note">Free trial<br>iPhone</span>
          </div>
        </section>
      </div>
    </article>

    <section class="section section-tint related">
      <div class="wrap">
        <div class="head"><p class="kicker">Keep reading</p><h2>More on sprint technique.</h2></div>
        <div class="blog-grid">
{related_html}
        </div>
      </div>
    </section>
  </main>

{footer(up)}"""


def card(p, up, h="h2"):
    return f"""          <a class="blog-card" href="{up}blog/{p['slug']}/">
            <span class="blog-card-img"><img src="{up}{p['image']}" alt="" width="{p['image_w']}" height="{p['image_h']}" loading="lazy"{focus(p)}></span>
            <span class="label">{esc(p['kicker'])} · {p['minutes']} min read</span>
            <{h}>{esc(p['title'])}</{h}>
            <p>{esc(p['description'])}</p>
          </a>"""


def index_page(posts):
    up = "../"
    url = f"{SITE}/blog/"
    title = "Sprint technique blog — SprintVision"
    description = ("Research-backed guides to sprint technique: block starts, acceleration, "
                   "top-speed mechanics, step length and frequency, and how to film your runs.")
    extra = ld({
        "@context": "https://schema.org",
        "@type": "Blog",
        "name": "SprintVision blog",
        "description": description,
        "url": url,
        "publisher": PUBLISHER,
        "blogPost": [{
            "@type": "BlogPosting",
            "headline": p["title"],
            "url": f"{SITE}/blog/{p['slug']}/",
            "datePublished": p["date"],
        } for p in posts],
    })
    cards = "\n".join(card(p, up) for p in posts)
    return f"""{head(title, description, url, 'assets/og-image.jpg', up, extra=extra)}
<body class="blog">
{header(up)}

  <main>
    <section class="blog-intro">
      <div class="wrap">
        <p class="kicker">Blog</p>
        <h1>Sprint faster, one step at a time.</h1>
        <p>What the research says good sprinters do, from the set position to top speed, and how to check it in your own running.</p>
      </div>
    </section>
    <section class="blog-list">
      <div class="wrap">
        <div class="blog-grid">
{cards}
        </div>
      </div>
    </section>
  </main>

{footer(up)}"""


def sitemap(posts):
    today = max(p.get("updated", p["date"]) for p in posts)
    rows = [(f"{SITE}/{path}", None, pri) for path, pri in PAGES]
    rows.append((f"{SITE}/blog/", today, "0.8"))
    rows += [(f"{SITE}/blog/{p['slug']}/", p.get("updated", p["date"]), "0.7") for p in posts]
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, mod, pri in rows:
        out.append("  <url>")
        out.append(f"    <loc>{loc}</loc>")
        if mod:
            out.append(f"    <lastmod>{mod}</lastmod>")
        out.append(f"    <priority>{pri}</priority>")
        out.append("  </url>")
    out.append("</urlset>")
    return "\n".join(out) + "\n"


def llms(posts):
    lines = [
        "# SprintVision",
        "",
        "> SprintVision is an iPhone app for sprinters and coaches. You film one sprint (a block start,",
        "> acceleration or flying run) at normal speed, and it tracks the whole body, measures every step",
        "> (length, ground contact, flight time, speed, step frequency) and rates your positions against",
        "> targets from published sprint biomechanics research, with a coaching cue for anything outside",
        "> the range. Free trial, then a subscription.",
        "",
        "- It works side-on, handheld while following the run, or from behind; the camera can move.",
        "- Rated: set position (front and rear hip and knee, trunk), torso lean, shin angle at touchdown,",
        "  knee angle at touchdown, knee lift, heel recovery, arm swing, elbow angle and step frequency,",
        "  with separate targets for the drive phase and upright running where they apply.",
        "- Ground contact and flight times are shown as estimates (phone video is usually 30 fps).",
        "- Also: a training calendar, session tracking with rest timers, PDF reports and video export.",
        "- Plans: Athlete (1 athlete), Coach (up to 5), Club (up to 25), custom plans for more.",
        "- What athletes say: \"Everything is very clear, which is important during sessions so you're not",
        "  wasting time or getting stressed about figuring out what the analysis says.\" (Israel Olatunde,",
        "  100 m national record holder, European 100 m finalist)",
        "",
        f"App Store: {STORE}",
        "",
        "## Pages",
        "",
        f"- [Home]({SITE}/): what the app does, with a real analysed block start",
        f"- [Blog]({SITE}/blog/): research-backed sprint technique guides",
        f"- [Contact]({SITE}/contact.html)",
        "",
        "## Blog posts",
        "",
    ]
    lines += [f"- [{p['title']}]({SITE}/blog/{p['slug']}/): {p['description']}" for p in posts]
    return "\n".join(lines) + "\n"


def main():
    posts = load_posts()
    slugs = {p["slug"] for p in posts}
    # Remove pages for posts that were renamed or deleted.
    for d in (ROOT / "blog").glob("*/"):
        if d.name not in slugs and (d / "index.html").exists():
            (d / "index.html").unlink()
            d.rmdir()
    for p in posts:
        missing = set(p.get("related", [])) - slugs
        if missing:
            raise SystemExit(f"{p['slug']}: unknown related {missing}")
        out = ROOT / "blog" / p["slug"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(post_page(p, posts))
    (ROOT / "blog" / "index.html").write_text(index_page(posts))
    (ROOT / "sitemap.xml").write_text(sitemap(posts))
    (ROOT / "llms.txt").write_text(llms(posts))
    print(f"Built {len(posts)} posts")


if __name__ == "__main__":
    main()
