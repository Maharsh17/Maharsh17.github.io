#!/usr/bin/env bash
# Verification harness for the site. Exits non-zero on any failure.
set -uo pipefail
cd "$(dirname "$0")" || exit 1

PORT=8899
FAIL=0
fail() { echo "FAIL: $*"; FAIL=1; }

PAGES="index.html 404.html projects/index.html experience/index.html blog/index.html \
       map/index.html contact/index.html quit/index.html"
POSTS=$(ls blog/*/index.html 2>/dev/null | grep -v '^blog/index.html$')

# 1. Required pages exist
for p in $PAGES; do
  [ -f "$p" ] || fail "missing page $p"
done

# 2. Retired pages are gone
# Flat page files, replaced by folders with clean URLs
for p in game.html deletegame.html language.html notifications.html loadgame.html missions.html \
         hud.html stats.html weapons.html projects.html experience.html blog.html \
         map.html options.html quitgame.html; do
  [ -e "$p" ] && fail "retired page still present: $p"
done

# 3. JavaScript syntax
for j in assets/js/*.js; do
  node --check "$j" >/dev/null 2>&1 || fail "syntax error in $j"
done

# 3b. The blog generator parses
# ast.parse rather than py_compile: writing bytecode is py_compile's whole job,
# so it ignores -B and left a __pycache__ in scripts/ on every verification run.
python3 -c 'import ast,sys; ast.parse(open(sys.argv[1]).read())' tools/build-blog.py 2>/dev/null \
  || fail "syntax error in tools/build-blog.py"

# 4. Data files are valid JSON
for d in assets/data/overrides.json assets/data/timecyc.json assets/data/places.json assets/data/vehicles.json; do
  [ -f "$d" ] || { fail "missing $d"; continue; }
  jq empty "$d" >/dev/null 2>&1 || fail "invalid JSON in $d"
done

# 4b. Every project override carries a band the renderer knows about, or it
# is silently dropped from the page.
BAD=$(jq -r 'to_entries[] | select((.value.category // "") | inside("research work,research software,personal") | not) | .key' assets/data/overrides.json 2>/dev/null)
[ -n "$BAD" ] && { echo "$BAD" | sed 's/^/FAIL: unknown category on /'; FAIL=1; }

# 4b2. Pages that need a library actually load it. A page rewrite dropped the
# MapLibre <script> from map.html and every other check still passed: the file
# was on disk, every remaining path resolved, and the page returned 200. The
# only symptom was an empty map.
grep -q 'maplibre/maplibre-gl.js' map/index.html || fail "map.html does not load maplibre-gl.js"
grep -q 'maplibre/maplibre-gl.css' map/index.html || fail "map.html does not load maplibre-gl.css"
grep -q 'js/map.js' map/index.html || fail "map.html does not load map.js"

# 4b3. Every page carries the persistent shell and the navigation script, or
# the music stops the moment a visitor leaves it.
for p in $PAGES $POSTS; do
  [ -f "$p" ] || continue
  grep -q 'id="shell" data-keep' "$p" || fail "$p has no persistent #shell"
  grep -q 'js/nav.js' "$p" || fail "$p does not load js/nav.js"
  grep -q 'id="theme"' "$p" || fail "$p has no audio element"
done

# 4c. Every page loads site.css. Markup can reference a .site-* class while
# the stylesheet defining it is never linked, which renders unstyled but still
# passes an asset-resolution check. That happened to index.html.
for p in $PAGES $POSTS; do
  [ -f "$p" ] || continue
  grep -q 'css/site.css' "$p" || fail "$p does not link css/site.css"
done

# 5. Every local href/src resolves, including the generated posts one level
# down, which reference ../assets rather than ./assets
BAD=$(for f in $PAGES $POSTS; do
  [ -f "$f" ] || continue
  d=$(dirname "$f")
  grep -oE '(href|src)="\.\.?/[^"]*"' "$f" | sed -E 's/^(href|src)="//; s/"$//' | sort -u | while read -r p; do
    t="$d/$p"
    # A clean-URL link points at a directory, which -e would call fine even if
    # the folder were empty. What makes it a page is the index.html inside.
    if [ "${p%/}" != "$p" ]; then
      [ -f "${t}index.html" ] || echo "$f -> $p has no index.html"
    else
      [ -e "$t" ] || echo "$f references missing $p"
    fi
  done
done)
[ -n "$BAD" ] && { echo "$BAD" | sed 's/^/FAIL: /'; FAIL=1; }

# 6. Every CSS url() resolves
BAD=$(for c in $(find assets -name '*.css' 2>/dev/null); do
  d=$(dirname "$c")
  grep -oE 'url\(["'"'"']?[^)"'"'"']+' "$c" | sed -E 's/url\(["'"'"']?//' \
    | grep -v '^data:' | sed 's/[?#].*//' | sort -u | while read -r u; do
      [ -e "$d/$u" ] || echo "$c references missing $u"
    done
done)
[ -n "$BAD" ] && { echo "$BAD" | sed 's/^/FAIL: /'; FAIL=1; }

# 7. No phone number leaked. Scoped to what a deployed site would serve, and
# excluding this file, which necessarily contains the pattern it searches for.
# Flattening the site to the repo root put docs/ and posts/ inside the served
# tree, so anything in them is publicly fetchable once deployed.
grep -rqn "717-461" --exclude=check.sh --exclude-dir=.git . 2>/dev/null \
  && fail "phone number present in the served tree"

# 8. Pages serve 200
lsof -ti :$PORT | xargs kill -9 2>/dev/null
python3 -m http.server $PORT >/dev/null 2>&1 &
SRV=$!
sleep 2
for p in $PAGES $POSTS; do
  [ -f "$p" ] || continue
  code=$(curl -s -o /dev/null -w '%{http_code}' "http://localhost:$PORT/$p")
  [ "$code" = "200" ] || fail "$p returned $code"
done
kill $SRV 2>/dev/null
wait $SRV 2>/dev/null

[ $FAIL -eq 0 ] && echo "ALL CHECKS PASSED"
exit $FAIL
