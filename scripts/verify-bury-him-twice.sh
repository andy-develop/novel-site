#!/usr/bin/env bash
# Verify Bury Him Twice on lyriq.top with retries (SSR intermittently 503s).
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
check() {
  local url="$1" desc="$2" want="$3"
  for i in 1 2 3 4 5 6 7 8; do
    resp=$(curl -s -o /tmp/vresp.html -w "%{http_code}" -A "$UA" --max-time 30 "$url")
    if [ "$resp" = "200" ]; then
      if grep -qi "$want" /tmp/vresp.html; then
        echo "OK  $desc -> $resp (contains '$want')"
        return 0
      else
        echo "WARN $desc -> 200 but missing '$want' (retry $i)"
      fi
    else
      echo "TRY $desc -> $resp (attempt $i)"
    fi
    sleep 5
  done
  echo "FAIL $desc -> last status $resp"
  return 1
}
check "https://lyriq.top/novel/bury-him-twice/1" "chapter 1 page" "Funeral for a Startup God"
check "https://lyriq.top/novel/bury-him-twice/30" "chapter 30 page" "Bury Him Twice"
check "https://lyriq.top/" "home page" "Bury Him Twice"
check "https://lyriq.top/novel/definitely-not-a-real-slug-xyz/1" "bogus slug" "404"
