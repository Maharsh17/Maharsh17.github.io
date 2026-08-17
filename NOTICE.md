# Notice

This project is not under a single license. Each part carries the license that
actually applies to it, in the directory that holds it.

## Map of licenses

| Part | Location | License | File |
|---|---|---|---|
| Original work | `scripts/`, `combined-gta/js/`, `combined-gta/css/site.css`, page markup, `combined-gta/data/`, `check.sh` | AGPL-3.0 | `LICENSE` |
| MapLibre GL JS 4.7.1 | `combined-gta/assets/maplibre/` | BSD-3-Clause, © MapLibre contributors | `combined-gta/assets/maplibre/LICENSE` |
| GTA SA menu recreation | `combined-gta/assets/menu/` | none declared, © J33sus | `combined-gta/assets/menu/LICENSE.md` |
| Notification library | `combined-gta/assets/notify/` | none declared, © J33sus | `combined-gta/assets/notify/LICENSE.md` |
| Decoded game textures | `combined-gta/assets/game/` | Rockstar Games, all rights reserved | `combined-gta/assets/game/README.md` |

The AGPL-3.0 in `LICENSE` covers only the first row. A license governs what its
author owns, so it does not extend to anything below that line.

## The two unlicensed dependencies

`assets/menu/` and `assets/notify/` come from public repositories that ship
no LICENSE file. Under default copyright that is all
rights reserved, which means no redistribution right is granted regardless of
what this repository's own LICENSE says.

This matters more than the Rockstar textures do, because those two are the
visual foundation of the whole site rather than two decorative images.

The alternatives are to ask the author to add a license, to replace those
assets, or to keep the site private.

## Modifications made to vendored code

Recorded here so the changes are not mistaken for upstream behaviour.

- `assets/notify/js/gtasa-notification*.js`: sound paths rewritten for this
  directory layout, and `Audio.play()` promise rejections caught. Browsers
  block audio before a user gesture, so the original threw unhandled
  rejections on every page load.
- `assets/menu/js/gtasamenu*.js` is no longer loaded by any linked page. It
  bound a hover handler to every `.menu-option` present when it ran, which
  missed rows rendered later, used a relative sound path that broke one
  directory down, and shared a single `Audio` so a fast pass down a list
  blipped once. `combined-gta/js/menu-sound.js` replaces it with one
  delegated listener. The file is left in place unmodified.

## Runtime services

`combined-gta/map.html` loads a MapTiler style at runtime. Map data is
© MapTiler and © OpenStreetMap contributors, attributed in the map control.

Address lookups during development used Nominatim,
© OpenStreetMap contributors.
