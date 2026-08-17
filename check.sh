#!/usr/bin/env bash
# Verification harness for combined-gta. Exits non-zero on any failure.
set -uo pipefail
cd "$(dirname "$0")/combined-gta" || exit 1

PORT=8899
FAIL=0
fail() { echo "FAIL: $*"; FAIL=1; }

PAGES="index.html loadgame.html stats.html weapons.html 404.html missions.html map.html hud.html options.html quitgame.html"

# 1. Required pages exist
for p in $PAGES; do
  [ -f "$p" ] || fail "missing page $p"
done

# 2. Retired pages are gone
for p in game.html deletegame.html language.html notifications.html; do
  [ -e "$p" ] && fail "retired page still present: $p"
done

# 3. JavaScript syntax
for j in js/*.js; do
  node --check "$j" >/dev/null 2>&1 || fail "syntax error in $j"
done

# 4. Data files are valid JSON
for d in data/projects.json data/overrides.json data/timecyc.json data/weapons.json data/places.json data/vehicles.json; do
  [ -f "$d" ] || { fail "missing $d"; continue; }
  jq empty "$d" >/dev/null 2>&1 || fail "invalid JSON in $d"
done

# 4b. Every page loads site.css. Markup can reference a .site-* class while
# the stylesheet defining it is never linked, which renders unstyled but still
# passes an asset-resolution check. That happened to index.html.
for p in $PAGES; do
  grep -q 'css/site.css' "$p" || fail "$p does not link css/site.css"
done

# 5. Every local href/src resolves
BAD=$(for f in *.html; do
  grep -oE '(href|src)="\./[^"]*"' "$f" | sed -E 's/^(href|src)="//; s/"$//' | sort -u | while read -r p; do
    [ -e "$p" ] || echo "$f references missing $p"
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
for p in $PAGES; do
  code=$(curl -s -o /dev/null -w '%{http_code}' "http://localhost:$PORT/$p")
  [ "$code" = "200" ] || fail "$p returned $code"
done
kill $SRV 2>/dev/null
wait $SRV 2>/dev/null

[ $FAIL -eq 0 ] && echo "ALL CHECKS PASSED"
exit $FAIL
