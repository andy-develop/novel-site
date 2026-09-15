#!/bin/bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
curl -s -A "$UA" --max-time 25 "https://lyriq.top/novel/where-the-smoke-went/1" -o /tmp/w1.html
echo "ch1 title: $(grep -o '<title>[^<]*</title>' /tmp/w1.html | head -1)"
curl -s -A "$UA" --max-time 25 "https://lyriq.top/novel/where-the-smoke-went/27" -o /tmp/w27.html
echo "ch27 title: $(grep -o '<title>[^<]*</title>' /tmp/w27.html | head -1)"
curl -s -A "$UA" --max-time 25 "https://lyriq.top/" -o /tmp/home.html
echo "home has book title: $(grep -c 'Where the Smoke Went' /tmp/home.html)"
echo "ch1 H1 in page: $(grep -o 'Chapter 1: Fan Favorite' /tmp/w1.html | head -1)"
echo "redirect for /99: $(curl -s -o /dev/null -w '%{redirect_url}' -A "$UA" 'https://lyriq.top/novel/where-the-smoke-went/99')"
