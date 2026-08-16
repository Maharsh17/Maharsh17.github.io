# Extracted game assets

These two PNGs are decoded from `models/fronten2.txd` in a retail Grand Theft
Auto: San Andreas install, using `scripts/extract-txd.py`.

| File | Source texture | Used by |
|---|---|---|
| `back6.png` | `fronten2.txd:back6` | `hud.html` corner art |
| `back7.png` | `fronten2.txd:back7` | `missions.html` corner art |

## Why only these two

The fan-made recreation in `assets/menu/images/` already ships `back2`,
`back3`, `back4`, `back5` and `back8` at identical resolutions, so re-extracting
those would add copyrighted bytes for no visual gain. `back6` and `back7` are
the only menu backgrounds the recreation does not include.

The recreation's `map.png` is 768x640, larger than the game's 512x512, so that
was not replaced either.

## Licensing

These are Rockstar Games' copyrighted assets, not fan-made recreations.
Everything else on this site is either original work or a fan recreation that
is distributable on its own terms.

They are isolated in this directory specifically so that removing them is one
`rm -rf` plus two edits:

- `missions.html` - point `.menu-image` back at `./assets/menu/images/back5.png`
- `css/site.css` - drop the `.site-hud-art` rule

Nothing else depends on them.
