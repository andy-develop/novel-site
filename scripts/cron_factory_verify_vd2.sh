#!/bin/bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
echo "=== bogus slug redirect target:"
curl -s -o /dev/null -w "%{redirect_url}\n" -A "$UA" --max-time 30 "https://lyriq.top/novel/definitely-not-a-real-slug/1"
echo "=== bookId on chapter 1 page:"
curl -s -A "$UA" --max-time 30 "https://lyriq.top/novel/viral-descent/1" | grep -o "bookId[^,;]*" | head -3
echo "=== bookId on chapter 27 page:"
curl -s -A "$UA" --max-time 30 "https://lyriq.top/novel/viral-descent/27" | grep -o "bookId[^,;]*" | head -3
