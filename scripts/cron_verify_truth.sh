#!/bin/bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
fetch() {
  local url="$1"
  local out="$2"
  for i in 1 2 3 4 5; do
    code=$(curl -s -o "$out" -w "%{http_code}" -A "$UA" --max-time 25 "$url")
    if [ "$code" = "200" ]; then echo "$code"; return; fi
    sleep 3
  done
  echo "$code"
}
c1=$(fetch "https://lyriq.top/novel/truth-score/1" /tmp/ts1.html)
t1=$(grep -o '<title>[^<]*</title>' /tmp/ts1.html | head -1)
echo "ch1 -> $c1 | $t1"
c2=$(fetch "https://lyriq.top/novel/truth-score/28" /tmp/ts28.html)
t2=$(grep -o '<title>[^<]*</title>' /tmp/ts28.html | head -1)
echo "ch28 -> $c2 | $t2"
ch=$(fetch "https://lyriq.top/" /tmp/tshome.html)
echo "home -> $ch | truth-score mentions: $(grep -c -i 'truth.score' /tmp/tshome.html)"
cb=$(fetch "https://lyriq.top/novel/definitely-not-a-real-slug-xyz/1" /tmp/tsbogus.html)
echo "bogus -> $cb"
