#!/usr/bin/env python3
"""Build the blog from markdown.

    src/posts/YYYY-MM-DD-slug.md  ->  blog/slug/index.html
                                  ->  blog/index.html (the index)

Stdlib only, on purpose. This runs on a laptop before a git push, not in a
build pipeline, so a dependency to install is a dependency to remember.

Usage:  python3 scripts/build-blog.py
"""

import html
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS = os.path.join(ROOT, "src", "posts")
SITE = ROOT
OUT = os.path.join(SITE, "blog")

MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN",
          "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]


# --- front matter ----------------------------------------------------------

def parse(path):
    """Split a post into its front matter dict and its markdown body."""
    with open(path, encoding="utf-8") as fh:
        text = fh.read()

    meta = {}
    body = text
    if text.startswith("---"):
        _, fm, body = text.split("---", 2)
        for line in fm.strip().split("\n"):
            if ":" not in line:
                continue
            key, val = line.split(":", 1)
            val = val.strip()
            if val in ("true", "false"):
                val = val == "true"
            meta[key.strip()] = val

    slug = os.path.basename(path)[:-3]
    # Filenames are date-prefixed so the directory sorts chronologically, but
    # the date is noise in a URL.
    meta["slug"] = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", slug)
    meta["path"] = path
    return meta, body.strip()


def should_publish(meta):
    """Decide whether a parsed post gets built into the site.

    Called once per file in blog/posts/. Returning False skips the post
    entirely: no page is written and it never appears on the index.
    """
    # Publish unless the post says otherwise. A missing draft field means the
    # post goes up: a forgotten field should not silently swallow finished
    # writing, and TEMPLATE.md ships with draft: true so the accident this
    # guards against cannot start from a copy of the template.
    # ponytail: no future-date scheduling. Add it the first time a post needs
    # to go up while you are asleep.
    return not meta.get("draft", False)


# --- markdown --------------------------------------------------------------

def inline(text):
    """Inline markdown, on already-escaped text.

    ponytail: code spans are substituted last, so **bold** inside `code`
    would still render bold. Nobody writes that; fix it if someone does.
    """
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    return text


def md_to_html(md):
    """A deliberately small markdown subset: what a blog post actually uses."""
    out = []
    lines = md.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("```"):
            i += 1
            code = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(html.escape(lines[i]))
                i += 1
            out.append("<pre><code>" + "\n".join(code) + "</code></pre>")
            i += 1
            continue

        if not stripped:
            i += 1
            continue

        if stripped in ("---", "***", "___"):
            out.append("<hr>")
            i += 1
            continue

        m = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if m:
            level = len(m.group(1)) + 1  # h1 is the page title, so ## -> h2
            level = min(level, 6)
            out.append("<h%d>%s</h%d>" % (level, inline(html.escape(m.group(2))), level))
            i += 1
            continue

        if stripped.startswith("> "):
            quote = []
            while i < len(lines) and lines[i].strip().startswith("> "):
                quote.append(inline(html.escape(lines[i].strip()[2:])))
                i += 1
            out.append("<blockquote><p>" + " ".join(quote) + "</p></blockquote>")
            continue

        if re.match(r"^[-*]\s+", stripped) or re.match(r"^\d+\.\s+", stripped):
            ordered = bool(re.match(r"^\d+\.\s+", stripped))
            tag = "ol" if ordered else "ul"
            items = []
            pattern = r"^\d+\.\s+" if ordered else r"^[-*]\s+"
            while i < len(lines) and re.match(pattern, lines[i].strip()):
                items.append("<li>" + inline(html.escape(
                    re.sub(pattern, "", lines[i].strip()))) + "</li>")
                i += 1
            out.append("<%s>%s</%s>" % (tag, "".join(items), tag))
            continue

        para = []
        while i < len(lines) and lines[i].strip() and not re.match(
                r"^(#{1,4}\s|[-*]\s|\d+\.\s|>\s|```)", lines[i].strip()):
            para.append(inline(html.escape(lines[i].strip())))
            i += 1
        out.append("<p>" + " ".join(para) + "</p>")

    return "\n".join(out)


# --- page templates --------------------------------------------------------

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<meta http-equiv="X-UA-Compatible" content="IE=edge">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<title>%(title)s</title>
	<link rel="icon" type="image/png" sizes="32x32" href="%(up)sassets/vendor/menu/images/favicon-32x32.png">
	<meta name="description" content="%(desc)s">
	<link rel="stylesheet" href="%(up)sassets/vendor/menu/fonts/myfonts.min.css">
	<link rel="stylesheet" href="%(up)sassets/vendor/menu/css/normalize.min.css">
	<link rel="stylesheet" href="%(up)sassets/vendor/menu/css/gtasamenu.min.css">
	<link rel="stylesheet" href="%(up)sassets/vendor/notify/css/gtasa-notification.min.css">
	<link rel="stylesheet" href="%(up)sassets/css/site.css">
</head>
<body data-section="brief" class="container site-tall">
	<header class="menu-header">
		<h1 class="menu-title">%(heading)s</h1>
		<div class="menu-subtitle">%(subtitle)s</div>
		<div style="background-image: url('%(up)sassets/game/fronten2/back5.png');" class="menu-image"></div>
	</header>
"""

FOOT = """	<footer class="menu-footer">
		<span class="menu-option menu-option--back"><a href="%(back)s">back</a></span>
	</footer>
	<div id="shell" data-keep>
		<div id="player" class="site-player">
			<button type="button" class="site-player-play" aria-label="Play theme">
				<img class="site-player-art" src="%(up)sassets/game/fronten1/radio_bounce.png" alt="">
				<span class="site-player-glyph">&#9654;</span>
			</button>
			<span class="site-player-bar"><span class="site-player-fill"></span></span>
		</div>
		<audio id="theme" preload="metadata" loop src="%(up)sassets/audio/theme.mp3"></audio>
	</div>
	<script src="%(up)sassets/vendor/notify/js/gtasa-notification.min.js" data-keep></script>
	<script src="%(up)sassets/js/sky.js" data-keep></script>
	<script src="%(up)sassets/js/cheats.js" data-keep></script>
	<script src="%(up)sassets/js/player.js" data-keep></script>
	<script src="%(up)sassets/js/nav.js" data-keep></script>
	<script src="%(up)sassets/js/menu-sound.js" data-keep></script>
	<script src="%(up)sassets/js/site.js"></script>
</body>
</html>
"""


def fmt_date(iso):
    y, m, d = str(iso).split("-")
    return "%02d %s %s" % (int(d), MONTHS[int(m) - 1], y)


def write(path, text):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    print("  wrote %s" % os.path.relpath(path, ROOT))


def build_post(meta, body):
    ctx = {
        "title": "Maharsh Jani - " + html.escape(str(meta["title"])),
        "desc": html.escape(str(meta.get("summary", ""))),
        "heading": html.escape(str(meta["title"])),
        "subtitle": fmt_date(meta["date"]),
        "up": "../../",
        "back": "../",
    }
    page = (HEAD % ctx) + (
        '	<main class="menu-content site-scroll">\n'
        '		<div class="site-prose site-post">\n'
        + md_to_html(body) + "\n"
        '		</div>\n'
        '	</main>\n'
    ) + (FOOT % ctx)
    slug_dir = os.path.join(OUT, meta["slug"])
    os.makedirs(slug_dir, exist_ok=True)
    write(os.path.join(slug_dir, "index.html"), page)


def build_index(posts):
    ctx = {
        "title": "Maharsh Jani - Blog",
        "desc": "Writing by Maharsh Jani",
        "heading": "Blog",
        "subtitle": "Select an entry to read:",
        "up": "../",
        "back": "../",
    }
    if posts:
        rows = []
        for meta in posts:
            rows.append(
                '<li class="menu-option menu-option--datagame">'
                '<a href="./%s/" title="%s">'
                '<span class="menu-option--datagame-left">%s</span>'
                '<span class="menu-option--datagame-right">%s</span>'
                '</a></li>' % (
                    meta["slug"],
                    html.escape(str(meta.get("summary", ""))),
                    html.escape(str(meta["title"])),
                    fmt_date(meta["date"]),
                )
            )
        body = '<ul class="menu-container">' + "".join(rows) + "</ul>"
    else:
        body = ('<ul class="menu-container"><li class="menu-option '
                'menu-option--datagame menu-option--datagame-blank">'
                '<a href="#">no entries yet</a></li></ul>')

    page = (HEAD % ctx) + (
        '	<main class="menu-content site-scroll">\n'
        '		<div class="site-rows site-measure">' + body + "</div>\n"
        '	</main>\n'
    ) + (FOOT % ctx)
    write(os.path.join(OUT, "index.html"), page)


def main():
    if not os.path.isdir(POSTS):
        sys.exit("no src/posts/ directory")
    os.makedirs(OUT, exist_ok=True)

    published = []
    for name in sorted(os.listdir(POSTS)):
        if not name.endswith(".md") or name == "TEMPLATE.md":
            continue
        meta, body = parse(os.path.join(POSTS, name))
        if not should_publish(meta):
            print("  skip   %s" % name)
            continue
        build_post(meta, body)
        published.append(meta)

    # Newest first on the index.
    published.sort(key=lambda m: str(m["date"]), reverse=True)
    build_index(published)
    print("%d post(s) published" % len(published))


if __name__ == "__main__":
    main()
