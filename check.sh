#!/usr/bin/env bash
# Verification harness for combined-gta. Exits non-zero on any failure.
set -uo pipefail
cd "$(dirname "$0")/combined-gta" || exit 1

PORT=8899
FAIL=0
fail() { echo "FAIL: $*"; FAIL=1; }

PAGES="index.html projects.html experience.html blog.html map.html options.html quitgame.html 404.html"

# 1. Required pages exist
for p in $PAGES; do
  [ -f "$p" ] || fail "missing page $p"
done

# 2. Retired pages are gone
for p in game.html deletegame.html language.html notifications.html loadgame.html missions.html \
         hud.html stats.html weapons.html; do
  [ -e "$p" ] && fail "retired page still present: $p"
done

# 3. JavaScript syntax
for j in js/*.js; do
  node --check "$j" >/dev/null 2>&1 || fail "syntax error in $j"
done

# 3b. The blog generator parses
python3 -m py_compile ../scripts/build-blog.py 2>/dev/null || fail "syntax error in scripts/build-blog.py"

# 4. Data files are valid JSON
for d in data/projects.json data/overrides.json data/timecyc.json data/places.json data/vehicles.json; do
  [ -f "$d" ] || { fail "missing $d"; continue; }
  jq empty "$d" >/dev/null 2>&1 || fail "invalid JSON in $d"
done

# 4b. Every project override carries a band the renderer knows about, or it
# is silently dropped from the page.
BAD=$(jq -r 'to_entries[] | select((.value.category // "") | inside("research work,research software,personal") | not) | .key' data/overrides.json 2>/dev/null)
[ -n "$BAD" ] && { echo "$BAD" | sed 's/^/FAIL: unknown category on /'; FAIL=1; }

# 4b2. Pages that need a library actually load it. A page rewrite dropped the
# MapLibre <script> from map.html and every other check still passed: the file
# was on disk, every remaining path resolved, and the page returned 200. The
# only symptom was an empty map.
grep -q 'maplibre/maplibre-gl.js' map.html || fail "map.html does not load maplibre-gl.js"
grep -q 'maplibre/maplibre-gl.css' map.html || fail "map.html does not load maplibre-gl.css"
grep -q 'js/map.js' map.html || fail "map.html does not load map.js"

# 4b3. Every page carries the persistent shell and the navigation script, or
# the music stops the moment a visitor leaves it.
for p in $PAGES blog/*.html; do
  [ -f "$p" ] || continue
  grep -q 'id="shell" data-keep' "$p" || fail "$p has no persistent #shell"
  grep -q 'js/nav.js' "$p" || fail "$p does not load js/nav.js"
  grep -q 'id="theme"' "$p" || fail "$p has no audio element"
done

# 4c. Every page loads site.css. Markup can reference a .site-* class while
# the stylesheet defining it is never linked, which renders unstyled but still
# passes an asset-resolution check. That happened to index.html.
for p in $PAGES blog/*.html; do
  [ -f "$p" ] || continue
  grep -q 'css/site.css' "$p" || fail "$p does not link css/site.css"
done

# 5. Every local href/src resolves, including the generated posts one level
# down, which reference ../assets rather than ./assets
BAD=$(for f in *.html blog/*.html; do
  [ -f "$f" ] || continue
  d=$(dirname "$f")
  grep -oE '(href|src)="\.\.?/[^"]*"' "$f" | sed -E 's/^(href|src)="//; s/"$//' | sort -u | while read -r p; do
    [ -e "$d/$p" ] || echo "$f references missing $p"
  done
done)
[ -n "$BAD" ] && { echo "$BAD" | sed 's/^/FAIL: /'; FAIL=1; }

# 6. Every CSS url() resolves
BAD=$(for c in $(find assets css -name '*.css' 2>/dev/null); do
  d=$(dirname "$c")
  grep -oE 'url\(["'"'"']?[^)"'"'"']+' "$c" | sed -E 's/url\(["'"'"']?//' \
    | grep -v '^data:' | sed 's/[?#].*//' | sort -u | while read -r u; do
      [ -e "$d/$u" ] || echo "$c references missing $u"
    done
done)
[ -n "$BAD" ] && { echo "$BAD" | sed 's/^/FAIL: /'; FAIL=1; }

# 7. No phone number leaked
grep -rqn "717-461" . 2>/dev/null && fail "phone number present on site"

# 8. Pages serve 200
lsof -ti :$PORT | xargs kill -9 2>/dev/null
python3 -m http.server $PORT >/dev/null 2>&1 &
SRV=$!
sleep 2
for p in $PAGES blog/*.html; do
  [ -f "$p" ] || continue
  code=$(curl -s -o /dev/null -w '%{http_code}' "http://localhost:$PORT/$p")
  [ "$code" = "200" ] || fail "$p returned $code"
done
kill $SRV 2>/dev/null
wait $SRV 2>/dev/null

[ $FAIL -eq 0 ] && echo "ALL CHECKS PASSED"
exit $FAIL
