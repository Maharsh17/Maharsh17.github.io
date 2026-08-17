# Notice

No single license covers this project. Each part carries its own.

| Part | Location | License |
|---|---|---|
| Original work | `js/`, `css/`, `data/`, page markup, `scripts/`, `check.sh` | AGPL-3.0, see `LICENSE` |
| MapLibre GL JS 4.7.1 | `assets/maplibre/` | BSD-3-Clause, © MapLibre contributors |
| GTA SA menu recreation | `assets/menu/` | **none declared**, © J33sus |
| Notification library | `assets/notify/` | **none declared**, © J33sus |
| Decoded game textures | `assets/game/` | Rockstar Games, all rights reserved |

`LICENSE` covers row 1 only. It cannot grant rights to work it does not own.

**The two unlicensed rows matter most.** No LICENSE file means all rights
reserved, so no redistribution right exists whatever this repo's own license
says, and those two are the visual foundation of the site. Options: ask the
author to add a license, replace them, or keep the site private.

## Vendored code, modified

- `assets/notify/js/gtasa-notification*.js` - sound paths rewritten for this
  layout; `Audio.play()` rejections caught, since browsers block audio before
  a user gesture and the original threw on every page load.
- `assets/menu/js/gtasamenu*.js` - unmodified, but no longer loaded.
  `js/menu-sound.js` replaces it.

## Runtime services

`map.html` loads a MapTiler style. Map data © MapTiler and © OpenStreetMap
contributors, attributed in the map control. Development geocoding used
Nominatim, © OpenStreetMap contributors.
