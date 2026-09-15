#!/bin/bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
BASE="https://lyriq.top"
check() {
  local url="$1"; local label="$2"; local code=""
  for i in 1 2 3 4 5; do
    code=$(curl -s -o /tmp/v_page.html -w "%{http_code}" -A "$UA" "$url")
    [ "$code" = "200" ] && break
    sleep 3
  done
  echo "$label: HTTP $code  $url"
}
check "$BASE/novel/green-gables-is-trending/1" "ch1"
check "$BASE/novel/green-gables-is-trending/30" "ch30"
check "$BASE/novel/green-gables-is-trending/garbage-slug-xyz" "bogus"
check "$BASE/" "home"
echo "--- ch1 title tag ---"
curl -s -A "$UA" "$BASE/novel/green-gables-is-trending/1" | grep -oE '<title>[^<]*</title>' | head -1
echo "--- home contains book title ---"
curl -s -A "$UA" "$BASE/" | grep -o "Green Gables Is Trending" | head -1
