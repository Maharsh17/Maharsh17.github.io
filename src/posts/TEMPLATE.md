---
title: The title, in plain sentence case
date: 2026-08-17
summary: One sentence. This is the only thing shown on the blog index, so make it say something.
draft: true
---

Copy this file into `posts/` and rename it `YYYY-MM-DD-some-slug.md`.
The filename's slug becomes the URL, so `2026-08-17-why-i-hate-yaml.md`
publishes at `/blog/why-i-hate-yaml.html`.

Then run:

```
python3 scripts/build-blog.py
```

## What you can write

Headings with `##` and `###`. Paragraphs separated by a blank line.

- Bullet lists
- with `-`

1. Numbered lists
2. with `1.`

Inline you get **bold**, *italic*, `code`, and [links](https://example.com).

> Blockquotes with `>`.

Fenced code blocks with triple backticks.

---

Set `draft: false` when it is ready to go up.
