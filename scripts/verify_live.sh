#!/bin/bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
check() {
  local url="$1" out="$2"
  local code="" i
  for i in 1 2 3 4 5 6 7 8; do
    code=$(curl -s -o "$out" -w "%{http_code}" -A "$UA" --max-time 25 "$url")
    if [ "$code" = "200" ]; then break; fi
    sleep 3
  done
  echo "$code"
}
for url in "https://lyriq.top/novel/thirteen-confessions/1" "https://lyriq.top/novel/thirteen-confessions/30"; do
  code=$(check "$url" /tmp/page.html)
  title=$(grep -o '<title>[^<]*</title>' /tmp/page.html | head -1)
  bytes=$(wc -c < /tmp/page.html)
  echo "$url -> $code | $bytes bytes | $title"
done
code=$(check "https://lyriq.top/" /tmp/home.html)
echo "home -> $code | $(wc -c < /tmp/home.html) bytes | title hits: $(grep -c 'Thirteen Confessions' /tmp/home.html)"
code=$(curl -s -o /dev/null -w "%{http_code}" -A "$UA" --max-time 25 "https://lyriq.top/novel/this-slug-does-not-exist-xyz/1")
echo "bogus slug -> $code"
