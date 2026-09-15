#!/bin/bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
for n in 1 5 26 27; do
  code=""
  for i in 1 2 3 4 5 6; do
    code=$(curl -s -o /tmp/p.html -w "%{http_code}" -A "$UA" --max-time 25 "https://lyriq.top/novel/the-painted-moonstone/$n")
    if [ "$code" = "200" ]; then break; fi
    sleep 3
  done
  title=$(grep -o '<title>[^<]*</title>' /tmp/p.html | head -1)
  echo "ch$n -> $code | $title"
done
