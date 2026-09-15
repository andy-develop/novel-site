#!/bin/bash
# Verify STOLEN FIRE on lyriq.top (retry loop for flaky SSR)
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
check() {
  local url="$1" want="$2"
  for i in 1 2 3 4 5 6; do
    out=$(curl -s -A "$UA" -o /tmp/vf_body.html -w "%{http_code}" "$url")
    if [ "$out" = "200" ] || [ "$out" = "404" ]; then
      echo "$url -> HTTP $out"
      return 0
    fi
    sleep 3
  done
  echo "$url -> HTTP $out (after retries)"
}
check "https://lyriq.top/novel/stolen-fire/1" 200
echo "  ch1 title tag: $(grep -o '<title>[^<]*</title>' /tmp/vf_body.html | head -1)"
check "https://lyriq.top/novel/stolen-fire/28" 200
echo "  ch28 title tag: $(grep -o '<title>[^<]*</title>' /tmp/vf_body.html | head -1)"
check "https://lyriq.top/" 200
grep -o 'STOLEN FIRE' /tmp/vf_body.html | head -1 && echo "  homepage contains STOLEN FIRE" || echo "  !! homepage missing STOLEN FIRE"
check "https://lyriq.top/novel/definitely-not-a-real-slug-xyz/1" 404
