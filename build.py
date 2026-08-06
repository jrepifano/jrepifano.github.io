#!/usr/bin/env python3
"""Build jrepifano.github.io. Standard library only, no Jekyll, no dependencies.

    python3 build.py

Reads _data/cv.json and writes index.html, cv/index.html and research/index.html.
Research artifacts under research/<slug>/index.html are self-contained pages that
this script does not touch; it only lists them, from the "research" array in
cv.json. That keeps each artifact immune to site-wide CSS changes.

A .nojekyll file is written so GitHub Pages serves the tree verbatim.
"""
import html
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / "_data" / "cv.json").read_text())

DESC = ("Jacob Epifano, machine learning researcher and engineer. "
        "Evaluation infrastructure for LLM systems, singular learning theory, "
        "influence functions and interpretability.")


def esc(s):
    return html.escape(str(s), quote=False)


def shell(title, body, *, page, description=DESC, extra_head=""):
    nav_items = [("/research/", "Research", "research"),
                 ("/cv/", "CV", "cv"),
                 ("https://github.com/jrepifano", "GitHub", None)]
    cur = ' aria-current="page"'
    links = "".join(
        '<a href="{}"{}>{}</a>'.format(h, cur if (k and k == page) else "", t)
        for h, t, k in nav_items)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<meta name="author" content="Jacob Epifano">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:type" content="website">
<link rel="stylesheet" href="/assets/site.css">
{extra_head}</head>
<body>
<nav class="nav">
  <a class="home" href="/">Jacob Epifano</a>
  <span class="links">{links}</span>
</nav>
<div class="wrap">
{body}
</div>
<footer class="site">
  <span>Jacob Epifano</span>
  <a href="mailto:{DATA['email']}">{DATA['email']}</a>
  <a href="https://github.com/jrepifano">GitHub</a>
  <a href="https://linkedin.com/in/jrepifano/">LinkedIn</a>
  <span style="margin-left:auto">Built with a 200-line Python script. No trackers.</span>
</footer>
</body>
</html>
"""



def series(r):
    """Optional sequence marker, e.g. "Part 1 of 2". Absent for standalone notes."""
    return f'<span class="series">{esc(r["series"])}</span>' if r.get("series") else ""

# --------------------------------------------------------------------- landing
def page_index():
    d = DATA
    contacts = " ".join(
        f'<a href="{l["href"]}">{esc(l["label"])}</a>' for l in d["links"])
    research = "".join(f"""
    <div class="entry">
      <div class="entry-head">
        <div class="t"><a href="{r['href']}">{esc(r['title'])}</a></div>
        {series(r)}<div class="when">{esc(r['date'])}</div>
      </div>
      <div class="desc">{esc(r['summary'])}</div>
    </div>""" for r in d["research"])

    pubs = ""
    for g in d["publications"]:
        items = "".join(f"""
      <div class="pub">
        <div class="t">{esc(p['title'])}</div>
        <div class="m"><span>{esc(p['venue'])}, {esc(p['year'])}</span>"""
                        + (f'<a href="{p["pdf"]}">PDF</a>' if p.get("pdf") else "")
                        + (f'<a href="{p["arxiv"]}">arXiv</a>' if p.get("arxiv") else "")
                        + "</div>\n      </div>" for p in g["items"])
        pubs += f'\n    <div class="pubgroup"><div class="g">{esc(g["group"])}</div>{items}</div>'

    body = f"""<div class="rule-top"></div>
  <h1 class="sr-only">{esc(d['name'])}</h1>
  <div class="intro">
    <img class="portrait" src="/assets/headshot.jpg" width="132" height="132"
         alt="Jacob Epifano">
    <div class="intro-text">
      <p class="role">{esc(d['title'])} &middot; {esc(d['location'])}</p>
      <p class="lede">{esc(d['summary'])}</p>
      <div class="contact-row">
        <a href="mailto:{d['email']}">{d['email']}</a>{contacts}
      </div>
    </div>
  </div>

  <section class="block">
    <h2>Research and writing</h2>
    {research}
  </section>

  <section class="block">
    <h2>Publications</h2>
    {pubs}
  </section>

  <section class="block">
    <h2>Currently</h2>
    <div class="col">
      <p>{esc(d['title'])} at {esc(d['experience'][0]['org'])}, building evaluation
      and observability infrastructure for production LLM systems. Full history on
      the <a href="/cv/">CV</a>.</p>
    </div>
  </section>"""
    return shell("Jacob Epifano", body, page="home")


# ------------------------------------------------------------------------- cv
def page_cv():
    d = DATA
    contacts = " ".join(
        f'<a href="{l["href"]}">{esc(l["label"])}</a>' for l in d["links"])

    exp = ""
    for e in d["experience"]:
        inner = ""
        if "groups" in e:
            for g in e["groups"]:
                lis = "".join(f"<li>{esc(b)}</li>" for b in g["bullets"])
                inner += f'<div class="sub">{esc(g["label"])}</div><ul>{lis}</ul>'
        else:
            lis = "".join(f"<li>{esc(b)}</li>" for b in e["bullets"])
            inner = f"<ul>{lis}</ul>"
        exp += f"""
    <div class="entry">
      <div class="entry-head">
        <div class="t">{esc(e['role'])}</div>
        <div class="when">{esc(e['time'])}</div>
      </div>
      <div class="org">{esc(e['org'])}</div>
      {inner}
    </div>"""

    skills = "".join(f"""
    <div class="skill">
      <div class="k">{esc(s['label'])}</div>
      <div class="v">{esc(s['text'])}</div>
    </div>""" for s in d["skills"])

    edu = "".join(f"""
    <div class="entry">
      <div class="entry-head">
        <div class="t">{esc(e['degree'])}</div>
        <div class="when">{esc(e['time'])}</div>
      </div>
      <div class="org">{esc(e['org'])}</div>
    </div>""" for e in d["education"])

    research = "".join(f"""
    <div class="entry">
      <div class="entry-head">
        <div class="t"><a href="{r['href']}">{esc(r['title'])}</a></div>
        {series(r)}<div class="when">{esc(r['date'])}</div>
      </div>
      <div class="desc">{esc(r['summary'])}</div>
    </div>""" for r in d["research"])

    pubs = ""
    for g in d["publications"]:
        items = "".join(f"""
      <div class="pub">
        <div class="t">{esc(p['title'])}</div>
        <div class="m"><span>{esc(p['venue'])}, {esc(p['year'])}</span>"""
                        + (f'<a href="{p["pdf"]}">PDF</a>' if p.get("pdf") else "")
                        + (f'<a href="{p["arxiv"]}">arXiv</a>' if p.get("arxiv") else "")
                        + "</div>\n      </div>" for p in g["items"])
        pubs += f'\n    <div class="pubgroup"><div class="g">{esc(g["group"])}</div>{items}</div>'

    body = f"""<div class="rule-top"></div>
  <div class="col">
    <h1>{esc(d['name'])}</h1>
    <p class="eyebrow" style="margin-top:8px">{esc(d['title'])}</p>
    <p class="lede">{esc(d['summary'])}</p>
    <div class="contact-row">
      <a href="mailto:{d['email']}">{d['email']}</a>
      <span>{esc(d['phone'])}</span>{contacts}
      <span>{esc(d['location'])}</span>
    </div>
    <p class="no-print" style="margin-top:18px;font-family:var(--font-mono);font-size:.74rem;color:var(--ink-3)">
      Print this page for a PDF copy.
    </p>
  </div>

  <section class="block"><h2>Research and writing</h2>{research}</section>
  <section class="block"><h2>Experience</h2>{exp}</section>
  <section class="block"><h2>Core skills</h2>{skills}</section>
  <section class="block"><h2>Education</h2>{edu}</section>
  <section class="block"><h2>Publications</h2>{pubs}</section>"""
    return shell(f"CV | {d['name']}", body, page="cv",
                 description="Curriculum vitae of Jacob Epifano, Ph.D.")


# ------------------------------------------------------------------- research
def page_research():
    items = "".join(f"""
    <div class="entry">
      <div class="entry-head">
        <div class="t"><a href="{r['href']}">{esc(r['title'])}</a></div>
        {series(r)}<div class="when">{esc(r['date'])}</div>
      </div>
      <div class="desc">{esc(r['summary'])}</div>
    </div>""" for r in DATA["research"])
    body = f"""<div class="rule-top"></div>
  <div class="col">
    <h1>Research and writing</h1>
    <p class="lede">Notes and experiments, mostly on singular learning theory,
    interpretability, and what our measurement tools actually measure. Each is a
    self-contained page with its data and code linked.</p>
  </div>
  <section class="block">{items}</section>
  <section class="block">
    <h2>Papers</h2>
    <div class="col"><p>Peer-reviewed publications are listed on the
    <a href="/cv/">CV</a>, with PDFs.</p></div>
  </section>"""
    return shell("Research | Jacob Epifano", body, page="research",
                 description="Research notes and experiments by Jacob Epifano.")


def main():
    (ROOT / ".nojekyll").write_text("")
    (ROOT / "index.html").write_text(page_index())
    for sub, fn in (("cv", page_cv), ("research", page_research)):
        d = ROOT / sub
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(fn())
    n = len(DATA["research"])
    print(f"built: index.html, cv/, research/  ({n} research item{'s' if n != 1 else ''} listed)")
    for r in DATA["research"]:
        target = ROOT / r["href"].strip("/") / "index.html"
        print(f"  {'ok  ' if target.exists() else 'MISSING'} {r['href']}")


if __name__ == "__main__":
    main()
