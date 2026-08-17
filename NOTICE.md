# Notice

The AGPL-3.0 in `LICENSE` covers the original work in this repository: the
generators in `scripts/`, the site JavaScript in `combined-gta/js/`,
`combined-gta/css/site.css`, the page markup, the data files, and `check.sh`.

It does not and cannot cover the third-party components below. A license only
applies to what its author owns.

## Vendored components

| Component | Location | License |
|---|---|---|
| `gta-sa-hud-react` (built output) | `combined-gta/assets/hud/` | MIT, by MickMelon |
| MapLibre GL JS 4.7.1 | `combined-gta/assets/maplibre/` | BSD-3-Clause |
| `gtasamenu` CSS, JS, fonts, images | `combined-gta/assets/menu/` | no license declared, by J33sus |
| `gtasa-stats` CSS and fonts | `combined-gta/assets/stats/` | no license declared, by J33sus |
| `gtasa-notification.js` | `combined-gta/assets/notify/` | no license declared, by J33sus |

Three of the fan recreations ship **no license file at all**. Under default
copyright that means no redistribution right is granted, regardless of what
this repository's own LICENSE says. If this site is published, the clean fixes
are to ask those authors to add a license, or to replace those assets.

The React HUD is MIT, so its copyright notice must travel with it. That is
satisfied by this file plus the upstream LICENSE, without any on-page credit.

## Game assets

`combined-gta/assets/game/` contains textures decoded from a retail Grand Theft
Auto: San Andreas install. These are Rockstar Games' copyrighted assets, kept
for personal use. They are not covered by the AGPL and are not redistributable.

See `combined-gta/assets/game/README.md` for exactly which files ship and how
to remove them.

## Map data

`combined-gta/map.html` loads a MapTiler style at runtime. Map data is
© MapTiler and © OpenStreetMap contributors, attributed in the map control.

Geocoding during development used Nominatim, © OpenStreetMap contributors.
