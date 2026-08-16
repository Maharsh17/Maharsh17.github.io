#!/usr/bin/env python3
"""Generate a GTA San Andreas style pause-menu map of Champaign-Urbana.

Flat 2D cartography, no 3D, no shadows: white urban blocks, green parks, blue
water, dark grey road lines, SA radar-sprite landmark icons, legend, compass.

Geography is real. Every feature below carries approximate WGS84 coordinates
and is projected into the SVG viewport, so relative positions are correct even
though road geometry is simplified to a handful of waypoints per route. That
simplification is faithful to the source: SA's own pause map is stylised, not
survey-grade.

Usage:
    build-cu-map.py <out.svg>
"""
import sys

# Viewport. The map panel is square-ish; the legend sits to its right.
W, H = 1000, 720
MAP_W = 700
PAD = 12

# Bounding box over Champaign, Urbana and Savoy.
LAT_N, LAT_S = 40.150, 40.030
LON_W, LON_E = -88.310, -88.170

PALETTE = {
    "bg": "#0d1b1e",         # outside the city, near-black teal
    "block": "#e8e6dd",      # urban blocks, off-white
    "block2": "#d6d3c7",     # secondary blocks
    "park": "#3f7a3a",       # parks and rural
    "water": "#2f6ea8",      # rivers and lakes
    "road": "#3a3f42",       # major roads and highways
    "road_hi": "#6f7679",    # secondary roads
    "ink": "#d9dcd9",
    "gold": "#c2a22b",
}


def px(lon, lat):
    """WGS84 -> SVG coordinates inside the map panel."""
    x = (lon - LON_W) / (LON_E - LON_W) * (MAP_W - 2 * PAD) + PAD
    y = (LAT_N - lat) / (LAT_N - LAT_S) * (H - 2 * PAD) + PAD
    return round(x, 1), round(y, 1)


def esc(text):
    """XML-escape. Landmark names contain ampersands, which are invalid raw."""
    return (str(text).replace("&", "&amp;")
            .replace("<", "&lt;").replace(">", "&gt;"))


def path(points, close=False):
    d = " ".join(
        ("M" if i == 0 else "L") + f"{px(lon, lat)[0]},{px(lon, lat)[1]}"
        for i, (lon, lat) in enumerate(points)
    )
    return d + (" Z" if close else "")


# --- Urban footprints -------------------------------------------------------
# Rough built-up extents, drawn as flat blocks.
BLOCKS = [
    # Champaign, west of the campus
    [(-88.290, 40.135), (-88.238, 40.138), (-88.236, 40.092),
     (-88.288, 40.090)],
    # Urbana, east
    [(-88.225, 40.132), (-88.180, 40.130), (-88.180, 40.092),
     (-88.226, 40.094)],
    # Campus core between the two downtowns
    [(-88.240, 40.118), (-88.218, 40.118), (-88.218, 40.088),
     (-88.240, 40.088)],
    # North Champaign / Market Place
    [(-88.270, 40.150), (-88.232, 40.150), (-88.232, 40.136),
     (-88.270, 40.136)],
    # Savoy, south
    [(-88.262, 40.062), (-88.232, 40.062), (-88.232, 40.040),
     (-88.262, 40.040)],
]

# --- Parks and green space --------------------------------------------------
PARKS = [
    ("Crystal Lake Park", [(-88.206, 40.128), (-88.192, 40.128),
                           (-88.192, 40.118), (-88.206, 40.118)]),
    ("Hessel Park", [(-88.258, 40.098), (-88.248, 40.098),
                     (-88.248, 40.092), (-88.258, 40.092)]),
    ("West Side Park", [(-88.248, 40.118), (-88.242, 40.118),
                        (-88.242, 40.113), (-88.248, 40.113)]),
    ("Meadowbrook Park", [(-88.202, 40.078), (-88.186, 40.078),
                          (-88.186, 40.064), (-88.202, 40.064)]),
    ("Arboretum", [(-88.228, 40.100), (-88.216, 40.100),
                   (-88.216, 40.090), (-88.228, 40.090)]),
    # Rural fringe, south-west
    [(-88.310, 40.075), (-88.276, 40.075), (-88.276, 40.030), (-88.310, 40.030)],
]

# --- Water ------------------------------------------------------------------
WATER = [
    # Crystal Lake
    [(-88.203, 40.126), (-88.196, 40.126), (-88.196, 40.121), (-88.203, 40.121)],
]
# Boneyard Creek, west to east through downtown Champaign and campus
BONEYARD = [(-88.266, 40.116), (-88.250, 40.117), (-88.240, 40.115),
            (-88.228, 40.113), (-88.214, 40.112), (-88.200, 40.110)]

# --- Roads ------------------------------------------------------------------
HIGHWAYS = [
    ("I-57", [(-88.298, 40.150), (-88.297, 40.100), (-88.296, 40.030)]),
    ("I-74", [(-88.310, 40.128), (-88.270, 40.129), (-88.230, 40.131),
              (-88.180, 40.133), (-88.170, 40.134)]),
    ("I-72", [(-88.310, 40.052), (-88.280, 40.050), (-88.245, 40.047),
              (-88.200, 40.046), (-88.170, 40.046)]),
]

ROADS = [
    ("University Ave", [(-88.290, 40.1125), (-88.240, 40.1125),
                        (-88.200, 40.1120), (-88.176, 40.1118)]),
    ("Green St", [(-88.260, 40.1103), (-88.240, 40.1102),
                  (-88.220, 40.1100), (-88.196, 40.1098)]),
    ("Springfield Ave", [(-88.288, 40.1148), (-88.240, 40.1145),
                         (-88.196, 40.1142)]),
    ("Kirby / Florida Ave", [(-88.288, 40.0955), (-88.240, 40.0952),
                             (-88.190, 40.0950)]),
    ("Windsor Rd", [(-88.288, 40.0755), (-88.230, 40.0752), (-88.186, 40.0750)]),
    ("Neil St", [(-88.2435, 40.150), (-88.2435, 40.112), (-88.2437, 40.060),
                 (-88.2440, 40.032)]),
    ("Prospect Ave", [(-88.2640, 40.148), (-88.2642, 40.112), (-88.2645, 40.070)]),
    ("Mattis Ave", [(-88.2790, 40.145), (-88.2792, 40.110), (-88.2795, 40.075)]),
    ("Lincoln Ave", [(-88.2200, 40.140), (-88.2202, 40.112), (-88.2205, 40.070)]),
    ("Race St", [(-88.2040, 40.135), (-88.2042, 40.110), (-88.2045, 40.070)]),
    ("Cunningham Ave", [(-88.2070, 40.150), (-88.2085, 40.130), (-88.2095, 40.118)]),
    ("First St", [(-88.2380, 40.125), (-88.2382, 40.090)]),
]

# --- Landmarks --------------------------------------------------------------
# (name, lon, lat, radar sprite). Coordinates are real.
LANDMARKS = [
    ("Memorial Stadium",        -88.2360, 40.0995, "radar_Flag.png"),
    ("State Farm Center",       -88.2359, 40.0967, "radar_race.png"),
    ("Main Quad & Illini Union", -88.2272, 40.1092, "radar_school.png"),
    ("Krannert Center",         -88.2244, 40.1085, "radar_dateDisco.png"),
    ("Grainger Library",        -88.2270, 40.1121, "radar_qmark.png"),
    ("Research Park",           -88.2380, 40.0930, "radar_light.png"),
    ("Downtown Champaign",      -88.2434, 40.1164, "radar_propertyG.png"),
    ("Downtown Urbana",         -88.2073, 40.1106, "radar_police.png"),
    ("Crystal Lake Park",       -88.2003, 40.1234, "radar_saveGame.png"),
    ("Willard Airport",         -88.2782, 40.0392, "radar_airYard.png"),
]

ICON_DIR = "./assets/game/hud/"


def build():
    o = []
    a = o.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
      f'width="100%" height="100%" role="img" '
      f'aria-label="Champaign-Urbana in GTA San Andreas pause-map style" '
      f'shape-rendering="crispEdges" font-family="monospace">')

    a(f'<rect width="{W}" height="{H}" fill="{PALETTE["bg"]}"/>')
    a(f'<clipPath id="panel"><rect x="0" y="0" width="{MAP_W}" height="{H}"/></clipPath>')
    a('<g clip-path="url(#panel)">')

    # Rural green base
    a(f'<rect width="{MAP_W}" height="{H}" fill="#1d3a24"/>')

    # Parks
    for item in PARKS:
        pts = item[1] if isinstance(item, tuple) else item
        a(f'<path d="{path(pts, True)}" fill="{PALETTE["park"]}"/>')

    # Urban blocks
    for i, b in enumerate(BLOCKS):
        fill = PALETTE["block"] if i % 2 == 0 else PALETTE["block2"]
        a(f'<path d="{path(b, True)}" fill="{fill}"/>')

    # Water
    for w in WATER:
        a(f'<path d="{path(w, True)}" fill="{PALETTE["water"]}"/>')
    a(f'<path d="{path(BONEYARD)}" fill="none" stroke="{PALETTE["water"]}" '
      f'stroke-width="4"/>')

    # Secondary roads
    for _name, pts in ROADS:
        a(f'<path d="{path(pts)}" fill="none" stroke="{PALETTE["road"]}" '
          f'stroke-width="4"/>')

    # Highways, thicker
    for _name, pts in HIGHWAYS:
        a(f'<path d="{path(pts)}" fill="none" stroke="{PALETTE["road"]}" '
          f'stroke-width="9"/>')
        a(f'<path d="{path(pts)}" fill="none" stroke="{PALETTE["road_hi"]}" '
          f'stroke-width="3"/>')

    # Landmark icons
    for i, (name, lon, lat, icon) in enumerate(LANDMARKS, 1):
        x, y = px(lon, lat)
        a(f'<image href="{ICON_DIR}{icon}" x="{x - 9}" y="{y - 9}" '
          f'width="18" height="18"><title>{esc(name)}</title></image>')

    a('</g>')

    # Panel border
    a(f'<rect x="0.5" y="0.5" width="{MAP_W - 1}" height="{H - 1}" fill="none" '
      f'stroke="#7c7b7b" stroke-width="3"/>')

    # Compass rose, top-right of the map panel
    cx, cy = MAP_W - 46, 46
    a(f'<g><circle cx="{cx}" cy="{cy}" r="22" fill="rgba(0,0,0,.55)" '
      f'stroke="{PALETTE["ink"]}" stroke-width="1.5"/>'
      f'<path d="M{cx},{cy - 18} L{cx + 6},{cy} L{cx},{cy + 18} L{cx - 6},{cy} Z" '
      f'fill="{PALETTE["ink"]}"/>'
      f'<path d="M{cx},{cy - 18} L{cx + 6},{cy} L{cx - 6},{cy} Z" fill="#bf242a"/>'
      f'<text x="{cx}" y="{cy - 26}" fill="{PALETTE["ink"]}" font-size="11" '
      f'text-anchor="middle">N</text></g>')

    # Legend
    lx = MAP_W + 26
    a(f'<text x="{lx}" y="46" fill="{PALETTE["gold"]}" font-size="21" '
      f'letter-spacing="2">MAP LEGEND</text>')
    a(f'<text x="{lx}" y="68" fill="{PALETTE["ink"]}" font-size="11" '
      f'opacity=".65">CHAMPAIGN - URBANA, ILLINOIS</text>')

    y = 104
    for name, lon, lat, icon in LANDMARKS:
        a(f'<image href="{ICON_DIR}{icon}" x="{lx}" y="{y - 13}" '
          f'width="17" height="17"/>')
        a(f'<text x="{lx + 26}" y="{y}" fill="{PALETTE["ink"]}" font-size="13">'
          f'{esc(name)}</text>')
        y += 30

    # Scale note
    a(f'<text x="{lx}" y="{H - 26}" fill="{PALETTE["ink"]}" font-size="10" '
      f'opacity=".5">Real coordinates, simplified road geometry</text>')

    a('</svg>')
    return "\n".join(o)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    svg = build()
    open(sys.argv[1], 'w').write(svg)
    print(f"{sys.argv[1]}  {len(svg) // 1024}KB  "
          f"{len(LANDMARKS)} landmarks, {len(ROADS) + len(HIGHWAYS)} routes")
