#!/bin/bash
# Verify home page + 404 for Main Street Girl
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
code="000"
for i in 1 2 3 4 5; do
  code=$(curl -s -o /tmp/home.html -w "%{http_code}" -A "$UA" --max-time 25 "https://lyriq.top/")
  if [ "$code" = "200" ]; then break; fi
  sleep 4
done
count=$(grep -c "Main Street Girl" /tmp/home.html)
echo "home: $code | contains Main Street Girl: $count"
code2=$(curl -s -o /tmp/bogus.html -w "%{http_code}" -A "$UA" --max-time 25 "https://lyriq.top/novel/main-street-girl-bogus/1")
echo "bogus slug: $code2"
