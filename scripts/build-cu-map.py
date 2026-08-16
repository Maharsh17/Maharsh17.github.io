#!/usr/bin/env python3
"""Generate a GTA San Andreas style pause-menu map of Champaign-Urbana.

Flat 2D cartography, no 3D, no shadows.

The key idea, learned the hard way: a city map's texture IS its street grid.
Urban blocks are not drawn as polygons, they are what is left between streets.
So a dense minor grid is clipped to the built-up footprint and the blocks fall
out of it. An earlier version drew five big beige polygons plus fifteen roads
and read as abstract rectangles. This also happens to be accurate here, because
Champaign-Urbana is a grid city.

Landmark sprites are inlined as data URIs. External refs inside an SVG resolve
against the SVG's own URL rather than the host page, which silently 404s every
icon when embedded via <object>; inlining removes that whole class of problem.

Usage:
    build-cu-map.py <out.svg>
"""
import base64
import os
import sys

W, H = 1000, 720
MAP_W = 700
PAD = 10

# Bounding box over Champaign, Urbana and Savoy.
LAT_N, LAT_S = 40.150, 40.030
LON_W, LON_E = -88.310, -88.170

C = {
    "rural": "#24401f",
    "urban": "#e9e7de",
    "park": "#4b8b3f",
    "water": "#2f6ea8",
    "street": "#8e8b82",
    "road": "#3c4144",
    "hwy": "#2b2f31",
    "hwy_fill": "#7d8487",
    "panel": "#0d1b1e",
    "ink": "#d9dcd9",
    "gold": "#c2a22b",
}

ICON_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                        "combined-gta", "assets", "game", "hud")
_ICONS = {}


def icon_uri(name):
    if name not in _ICONS:
        with open(os.path.join(ICON_DIR, name), "rb") as fh:
            _ICONS[name] = "data:image/png;base64," + \
                base64.b64encode(fh.read()).decode("ascii")
    return _ICONS[name]


def px(lon, lat):
    x = (lon - LON_W) / (LON_E - LON_W) * (MAP_W - 2 * PAD) + PAD
    y = (LAT_N - lat) / (LAT_N - LAT_S) * (H - 2 * PAD) + PAD
    return round(x, 1), round(y, 1)


def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def path(points, close=False):
    d = " ".join(("M" if i == 0 else "L") + "%s,%s" % px(lo, la)
                 for i, (lo, la) in enumerate(points))
    return d + (" Z" if close else "")


# Built-up footprint. Champaign, campus and Urbana form one contiguous mass;
# Savoy sits detached to the south.
URBAN = [
    [(-88.294, 40.1430), (-88.246, 40.1465), (-88.228, 40.1440),
     (-88.196, 40.1400), (-88.178, 40.1330), (-88.176, 40.1080),
     (-88.184, 40.0900), (-88.214, 40.0840), (-88.236, 40.0800),
     (-88.262, 40.0850), (-88.288, 40.0930), (-88.296, 40.1150)],
    [(-88.264, 40.0660), (-88.230, 40.0665), (-88.228, 40.0380),
     (-88.262, 40.0375)],
]

# Willard Airport: apron plus two runways, so the icon sits on something.
AIRPORT = [(-88.2870, 40.0470), (-88.2690, 40.0468), (-88.2688, 40.0320),
           (-88.2868, 40.0322)]
RUNWAYS = [
    [(-88.2850, 40.0345), (-88.2710, 40.0450)],
    [(-88.2845, 40.0440), (-88.2715, 40.0350)],
]

PARKS = [
    ("Crystal Lake Park", [(-88.2075, 40.1290), (-88.1930, 40.1288),
                           (-88.1928, 40.1180), (-88.2072, 40.1182)]),
    ("Hessel Park", [(-88.2610, 40.0995), (-88.2500, 40.0993),
                     (-88.2498, 40.0925), (-88.2608, 40.0927)]),
    ("West Side Park", [(-88.2480, 40.1190), (-88.2415, 40.1189),
                        (-88.2414, 40.1140), (-88.2479, 40.1141)]),
    ("Meadowbrook Park", [(-88.2040, 40.0790), (-88.1860, 40.0788),
                          (-88.1858, 40.0640), (-88.2038, 40.0642)]),
    ("Arboretum", [(-88.2290, 40.1010), (-88.2160, 40.1008),
                   (-88.2158, 40.0910), (-88.2288, 40.0912)]),
    ("Illini Grove", [(-88.2200, 40.1055), (-88.2150, 40.1054),
                      (-88.2149, 40.1020), (-88.2199, 40.1021)]),
]

WATER = [
    [(-88.2035, 40.1265), (-88.1960, 40.1264), (-88.1958, 40.1210),
     (-88.2033, 40.1211)],
]
BONEYARD = [(-88.2660, 40.1163), (-88.2520, 40.1168), (-88.2430, 40.1160),
            (-88.2330, 40.1150), (-88.2200, 40.1145), (-88.2060, 40.1138),
            (-88.1900, 40.1132)]

HIGHWAYS = [
    ("I-57", [(-88.2985, 40.1500), (-88.2975, 40.1180), (-88.2965, 40.0800),
              (-88.2960, 40.0300)]),
    ("I-74", [(-88.3100, 40.1268), (-88.2820, 40.1285), (-88.2560, 40.1300),
              (-88.2300, 40.1318), (-88.2020, 40.1330), (-88.1700, 40.1340)]),
    ("I-72", [(-88.3100, 40.0520), (-88.2820, 40.0505), (-88.2500, 40.0480),
              (-88.2150, 40.0465), (-88.1700, 40.0460)]),
]

ARTERIALS = [
    ("University Ave", [(-88.2960, 40.1126), (-88.2400, 40.1126),
                        (-88.2000, 40.1121), (-88.1760, 40.1119)]),
    ("Green St", [(-88.2620, 40.1103), (-88.2400, 40.1102),
                  (-88.2200, 40.1100), (-88.1900, 40.1098)]),
    ("Springfield Ave", [(-88.2900, 40.1149), (-88.2400, 40.1146),
                         (-88.1900, 40.1143)]),
    ("Bradley Ave", [(-88.2900, 40.1290), (-88.2400, 40.1288), (-88.2100, 40.1286)]),
    ("Kirby / Florida", [(-88.2900, 40.0956), (-88.2400, 40.0953),
                         (-88.1880, 40.0950)]),
    ("Windsor Rd", [(-88.2900, 40.0756), (-88.2300, 40.0753), (-88.1870, 40.0751)]),
    ("Neil St", [(-88.2436, 40.1460), (-88.2436, 40.1120), (-88.2438, 40.0600),
                 (-88.2440, 40.0380)]),
    ("Prospect Ave", [(-88.2641, 40.1440), (-88.2643, 40.1120), (-88.2646, 40.0700)]),
    ("Mattis Ave", [(-88.2791, 40.1400), (-88.2793, 40.1100), (-88.2795, 40.0900)]),
    ("Lincoln Ave", [(-88.2201, 40.1380), (-88.2203, 40.1120), (-88.2206, 40.0850)]),
    ("Race St", [(-88.2041, 40.1330), (-88.2043, 40.1100), (-88.2046, 40.0780)]),
    ("Cunningham Ave", [(-88.2060, 40.1490), (-88.2075, 40.1300), (-88.2090, 40.1180)]),
    ("First St", [(-88.2381, 40.1250), (-88.2383, 40.0880)]),
    ("Wright St", [(-88.2310, 40.1180), (-88.2312, 40.0980)]),
]

LANDMARKS = [
    ("Memorial Stadium",         -88.2360, 40.0995, "radar_Flag.png"),
    ("State Farm Center",        -88.2359, 40.0967, "radar_race.png"),
    ("Main Quad & Illini Union", -88.2272, 40.1092, "radar_school.png"),
    ("Krannert Center",          -88.2244, 40.1085, "radar_dateDisco.png"),
    ("Grainger Library",         -88.2270, 40.1121, "radar_qmark.png"),
    ("Research Park",            -88.2380, 40.0930, "radar_light.png"),
    ("Downtown Champaign",       -88.2434, 40.1164, "radar_propertyG.png"),
    ("Downtown Urbana",          -88.2073, 40.1106, "radar_police.png"),
    ("Crystal Lake Park",        -88.2003, 40.1234, "radar_saveGame.png"),
    ("Willard Airport",          -88.2782, 40.0392, "radar_airYard.png"),
]

# Minor grid spacing in degrees, tuned so blocks read at this scale.
GRID_LON = 0.0032
GRID_LAT = 0.0026


def minor_grid():
    out = []
    lon = LON_W
    while lon <= LON_E:
        a, b = px(lon, LAT_N), px(lon, LAT_S)
        out.append(f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}"/>')
        lon += GRID_LON
    lat = LAT_S
    while lat <= LAT_N:
        a, b = px(LON_W, lat), px(LON_E, lat)
        out.append(f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}"/>')
        lat += GRID_LAT
    return "".join(out)


def build():
    o = []
    a = o.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" '
      f'xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" '
      f'width="100%" height="100%" role="img" '
      f'aria-label="Champaign-Urbana street map in GTA San Andreas style" '
      f'shape-rendering="crispEdges" font-family="monospace">')

    urban_d = " ".join(path(p, True) for p in URBAN)
    a('<defs>')
    a(f'<clipPath id="panel"><rect width="{MAP_W}" height="{H}"/></clipPath>')
    a(f'<clipPath id="urban"><path d="{urban_d}"/></clipPath>')
    a(f'<clipPath id="builtup"><path d="{urban_d}"/>'
      f'<path d="{path(AIRPORT, True)}"/></clipPath>')
    a('</defs>')

    a(f'<rect width="{W}" height="{H}" fill="{C["panel"]}"/>')
    a('<g clip-path="url(#panel)">')

    a(f'<rect width="{MAP_W}" height="{H}" fill="{C["rural"]}"/>')

    # Built-up area, then the grid carved across it. Blocks are the negative
    # space between streets, not shapes in their own right.
    a(f'<path d="{path(AIRPORT, True)}" fill="#4a4f45"/>')
    for r in RUNWAYS:
        a(f'<path d="{path(r)}" fill="none" stroke="{C["urban"]}" '
          f'stroke-width="3"/>')
    a(f'<path d="{urban_d}" fill="{C["urban"]}"/>')
    a(f'<g clip-path="url(#urban)" stroke="{C["street"]}" stroke-width="2.2">'
      f'{minor_grid()}</g>')

    # Parks sit above the grid so blocks do not show through them.
    for _n, pts in PARKS:
        a(f'<path d="{path(pts, True)}" fill="{C["park"]}"/>')

    for w in WATER:
        a(f'<path d="{path(w, True)}" fill="{C["water"]}"/>')
    a(f'<path d="{path(BONEYARD)}" fill="none" stroke="{C["water"]}" '
      f'stroke-width="3.5" stroke-linejoin="round"/>')

    # Arterials are city streets, so they stop at the city. Only the
    # interstates below are allowed to run out through farmland.
    a('<g clip-path="url(#builtup)">')
    for _n, pts in ARTERIALS:
        a(f'<path d="{path(pts)}" fill="none" stroke="{C["road"]}" '
          f'stroke-width="5" stroke-linecap="square"/>')
    a('</g>')

    # Highways: dark casing under a lighter core, as the game draws them.
    for _n, pts in HIGHWAYS:
        a(f'<path d="{path(pts)}" fill="none" stroke="{C["hwy"]}" '
          f'stroke-width="10" stroke-linejoin="round"/>')
    for _n, pts in HIGHWAYS:
        a(f'<path d="{path(pts)}" fill="none" stroke="{C["hwy_fill"]}" '
          f'stroke-width="3.5" stroke-linejoin="round"/>')

    for name, lon, lat, ic in LANDMARKS:
        x, y = px(lon, lat)
        u = icon_uri(ic)
        # Stadium and State Farm Center are ~16px apart at this scale, so the
        # halo is kept tight or the campus cluster fuses into one blob.
        a(f'<circle cx="{x}" cy="{y}" r="8.5" fill="rgba(0,0,0,.6)" '
          f'stroke="rgba(255,255,255,.25)" stroke-width="1"/>')
        a(f'<image href="{u}" xlink:href="{u}" x="{x - 6.5}" y="{y - 6.5}" '
          f'width="13" height="13"><title>{esc(name)}</title></image>')

    a('</g>')
    a(f'<rect x="1.5" y="1.5" width="{MAP_W - 3}" height="{H - 3}" fill="none" '
      f'stroke="#7c7b7b" stroke-width="3"/>')

    cx, cy = MAP_W - 44, 44
    a(f'<g><circle cx="{cx}" cy="{cy}" r="21" fill="rgba(0,0,0,.6)" '
      f'stroke="{C["ink"]}" stroke-width="1.5"/>'
      f'<path d="M{cx},{cy - 16} L{cx + 6},{cy + 4} L{cx - 6},{cy + 4} Z" fill="#bf242a"/>'
      f'<path d="M{cx},{cy + 16} L{cx + 6},{cy + 4} L{cx - 6},{cy + 4} Z" fill="{C["ink"]}"/>'
      f'<text x="{cx}" y="{cy - 24}" fill="{C["ink"]}" font-size="11" '
      f'text-anchor="middle">N</text></g>')

    lx = MAP_W + 26
    a(f'<text x="{lx}" y="46" fill="{C["gold"]}" font-size="21" '
      f'letter-spacing="2">MAP LEGEND</text>')
    a(f'<text x="{lx}" y="68" fill="{C["ink"]}" font-size="11" opacity=".65">'
      f'CHAMPAIGN - URBANA, ILLINOIS</text>')

    y = 106
    for name, _lo, _la, ic in LANDMARKS:
        u = icon_uri(ic)
        a(f'<image href="{u}" xlink:href="{u}" x="{lx}" y="{y - 14}" '
          f'width="18" height="18"/>')
        a(f'<text x="{lx + 28}" y="{y}" fill="{C["ink"]}" font-size="13">'
          f'{esc(name)}</text>')
        y += 30

    a(f'<text x="{lx}" y="{H - 42}" fill="{C["ink"]}" font-size="10" opacity=".5">'
      f'Real coordinates. Street grid generated;</text>')
    a(f'<text x="{lx}" y="{H - 28}" fill="{C["ink"]}" font-size="10" opacity=".5">'
      f'road geometry simplified, as the game does.</text>')

    a('</svg>')
    return "\n".join(o)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    svg = build()
    open(sys.argv[1], 'w').write(svg)
    print(f"{sys.argv[1]}  {len(svg) // 1024}KB  {len(LANDMARKS)} landmarks, "
          f"{len(ARTERIALS) + len(HIGHWAYS)} named routes")
