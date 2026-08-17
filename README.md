# Maharsh Jani

A personal site built as a playable-looking Grand Theft Auto: San Andreas
menu. Static HTML, no build step for the site itself, no framework, no
dependencies to install.

## Run It

```bash
python3 -m http.server 8899
```

Then open <http://localhost:8899>. Any static server works; there is nothing
to compile.

## Verify It

```bash
./check.sh
```

Thirteen checks: pages exist, retired pages stay gone, JavaScript parses, JSON
is valid, every project has a known band, `map.html` loads MapLibre, every
page carries the persistent shell, every link and CSS `url()` resolves, and
every page returns 200. It has caught real bugs that looked fine in a browser.

Needs `node`, `jq`, `curl` and `python3`.

## Layout

```
index.html          Main menu
projects.html       Research work / research software / personal
experience.html     Roles and education
blog.html           Post index, generated
map.html            Champaign-Urbana, with my places
options.html        Contact
quitgame.html       Yes or no
404.html            WASTED

posts/              Blog sources, markdown
blog/               Blog output, generated from posts/
js/                 Runtime, 8 files, no framework
css/site.css        The only stylesheet written for this site
data/               Content as JSON, edited by hand
assets/             Fonts, sprites, audio, vendored libraries
scripts/            build-blog.py, the one build step
```

## Write A Post

```bash
cp posts/TEMPLATE.md posts/2026-08-20-some-slug.md
# edit it, set draft: false
python3 scripts/build-blog.py
```

The filename's slug becomes the URL: `2026-08-20-some-slug.md` publishes at
`/blog/some-slug.html`. Front matter takes `title`, `date`, `summary` and
`draft`. A post with `draft: true` is skipped; a missing `draft` publishes.

The generator handles a small markdown subset: headings, lists, links, bold,
italic, inline code, fenced code blocks, blockquotes and rules. Standard
library only.

## Edit Content

Everything the site says about itself lives in `data/`, not in markup.

| File | Holds |
|---|---|
| `overrides.json` | Projects: band, order, name, one-liner, blurb |
| `places.json` | Map markers: name, detail, coordinates, radar sprite |
| `vehicles.json` | The garage line in each project's tooltip |
| `timecyc.json` | Eight sky keyframes from the game's `timecyc.dat` |

To add a project, add an entry to `overrides.json` with a `category` of
`research work`, `research software` or `personal`. Set `"noRepo": true` if
there is no repository, or `"private": true` if there is one but it is not
public; either way the row renders as plain text rather than a link that
would 404.

## How A Few Things Work

**Navigation.** `js/nav.js` intercepts internal links and swaps page content
into the live document instead of loading a new one. Chrome refuses
`audio.play()` on a fresh document, so this is the only way the music can
survive a page change. The pages are still real files: every URL works typed
in, shared, or with JavaScript off, and any failure falls back to a normal
navigation. One attribute decides what survives a swap, `data-keep`.

**The sky.** `js/sky.js` interpolates the game's own EXTRASUNNY_LA colour
keyframes by your local hour, so the strip across the top of every page warms
at sunset and goes near-black at midnight.

**Cheats.** Six real San Andreas codes work anywhere on the site. Nothing
advertises them.

## Licensing

Not one license. See `NOTICE.md`. Two vendored dependencies ship no license
at all, which matters if this is ever redistributed.

Game textures are Rockstar Games' and are used here for a personal fan
project.
