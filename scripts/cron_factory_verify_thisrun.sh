#!/usr/bin/env bash
# Verify Half Saint Half Fool on lyriq.top (retry up to 6x for SSR 503s)
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
check() {
  local url="$1" desc="$2"
  for i in 1 2 3 4 5 6; do
    code=$(curl -s -o /tmp/vf_body.html -w '%{http_code}' -A "$UA" --max-time 25 "$url")
    if [ "$code" = "200" ]; then
      echo "$desc: HTTP $code"
      return 0
    fi
    sleep 3
  done
  echo "$desc: FAILED final code=$code"
  return 1
}
check "https://lyriq.top/novel/half-saint-half-fool/1" "ch1"
grep -o '<title>[^<]*</title>' /tmp/vf_body.html | head -1
check "https://lyriq.top/novel/half-saint-half-fool/28" "ch28"
grep -o '<title>[^<]*</title>' /tmp/vf_body.html | head -1
check "https://lyriq.top/" "home"
grep -o 'Half Saint Half Fool' /tmp/vf_body.html | head -1
check "https://lyriq.top/novel/half-saint-half-fool/29" "bogus-ch29"
check "https://lyriq.top/novel/no-such-slug-xyz" "bogus-slug"
