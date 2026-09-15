#!/bin/bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
for url in "https://lyriq.top/novel/viral-descent/1" "https://lyriq.top/novel/viral-descent/27" "https://lyriq.top/" "https://lyriq.top/novel/definitely-not-a-real-slug/1"; do
  code=""
  for attempt in 1 2 3 4 5; do
    code=$(curl -s -o /tmp/vd_page.html -w "%{http_code}" -A "$UA" --max-time 30 "$url")
    if [ "$code" = "200" ] || [ "$code" = "404" ]; then break; fi
    sleep 3
  done
  echo "URL: $url -> HTTP $code"
  if [ "$code" = "200" ]; then
    grep -o "<title>[^<]*</title>" /tmp/vd_page.html | head -1
  fi
  if [ "$code" = "200" ] && [ "$url" = "https://lyriq.top/" ]; then
    echo "home contains 'Viral Descent': $(grep -c 'Viral Descent' /tmp/vd_page.html)"
  fi
done
