#!/bin/bash
# Verify THE DEEP END on lyriq.top with Chrome UA + retries (SSR is flaky).
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
check() {
  local url="$1" desc="$2" want="$3"
  for i in $(seq 1 8); do
    code=$(curl -s -o /tmp/vde.html -w '%{http_code}' -A "$UA" --max-time 25 "$url")
    size=$(wc -c < /tmp/vde.html)
    if [ "$code" = "200" ] && [ "$size" -gt 2000 ]; then
      echo "OK  $desc -> HTTP $code ($size bytes)"
      return 0
    fi
    sleep 4
  done
  echo "FAIL $desc -> HTTP $code ($size bytes) after 8 tries"
  return 1
}
check "https://lyriq.top/novel/the-deep-end/1" "ch1 page" 200
echo "  title: $(grep -o '<title>[^<]*</title>' /tmp/vde.html | head -1)"
check "https://lyriq.top/novel/the-deep-end/24" "ch24 page" 200
echo "  title: $(grep -o '<title>[^<]*</title>' /tmp/vde.html | head -1)"
check "https://lyriq.top/" "homepage" 200
if grep -q "The Deep End" /tmp/vde.html; then echo "OK  homepage contains 'The Deep End'"; else echo "FAIL homepage missing book title"; fi
check "https://lyriq.top/novel/this-slug-does-not-exist-xyz/1" "bogus slug" 200
if grep -qi "404\|not found" /tmp/vde.html; then echo "OK  bogus slug -> 404 content"; else echo "WARN bogus slug page code $? — check manually"; fi
