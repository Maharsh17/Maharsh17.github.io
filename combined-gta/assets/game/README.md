# Extracted game assets

Decoded from a retail Grand Theft Auto: San Andreas install by
`scripts/extract-txd.py`, which parses RenderWare texture dictionaries and
decompresses DXT1/DXT3 to PNG using only `struct` and `zlib`.

## What is here

| Folder | Count | Contents |
|---|---|---|
| `fronten1/` | 13 | 12 radio station logos, 128x128, plus a menu arrow |
| `fronten2/` | 8 | Menu backgrounds `back2` to `back8`, plus `map` |
| `fronten3/` | 2 | `back8_top` and `back8_right`, edge-extension tiles |
| `fronten_pc/` | 2 | `mouse` cursor and `crosshair` |
| `hud/` | 69 | All radar icons, weapon site reticles, `fist`, `radardisc` |
| `pcbtns/` | 4 | Directional button glyphs |
| `fonts/` | 2 | `font1` and `font2` glyph atlases, 512x512 |

Not extracted: `misc.txd` (car wheels), `particle.txd`, `effectsPC.txd`. Those
use uncompressed or palettized formats the decoder does not handle, and none of
them are useful on a website.

Also not extracted: `audio/` (3.2 GB), `movies/` (24 MB), and the `.img`
archives (1.1 GB of world models). Too large and irrelevant to a web page.

## What the site actually uses

Only two files, despite the size of the library:

| File | Used by |
|---|---|
| `fronten2/back6.png` | `hud.html` corner art |
| `fronten2/back7.png` | `missions.html` corner art |

The fan recreation in `assets/menu/images/` already ships `back2`, `back3`,
`back4`, `back5`, `back8` at identical resolutions, and its `map.png` is
larger than the game's (768x640 versus 512x512). Those were compared and left
alone rather than swapped for no visual gain.

The rest is a library to draw from, not dead weight that had to be used.

## Licensing

These are Rockstar Games' copyrighted assets, kept for personal use.
Everything else on this site is either original work or a fan-made recreation
distributable on its own terms.

They are isolated in this one directory so removal stays trivial:

```bash
rm -rf combined-gta/assets/game
```

Then point `missions.html` back at `./assets/menu/images/back5.png` and drop
the `.site-hud-art` rule from `css/site.css`. Nothing else depends on them.

## Related

`scripts/extract-gxt.py` dumps every in-game string to
`reference/gxt-strings.json` (16,588 strings, 127 tables). That file is
reference only and deliberately lives outside `combined-gta/`, so it is never
served.
