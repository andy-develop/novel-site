#!/usr/bin/env python3
"""Phase 7 verify: live pages for book 1509 (what-the-green-light-saw)."""
import urllib.request, sys, re

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

def fetch(url, tries=6):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                body = r.read().decode('utf-8', 'replace')
                return r.status, body
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}"
            if e.code != 503:
                return e.code, ""
        except Exception as e:
            last = str(e)
    return "FAIL", last or ""

urls = [
    ("ch1",  "https://lyriq.top/novel/what-the-green-light-saw/1"),
    ("ch30", "https://lyriq.top/novel/what-the-green-light-saw/30"),
    ("home", "https://lyriq.top/"),
    ("bogus","https://lyriq.top/novel/this-slug-does-not-exist-xyz/1"),
]

for name, url in urls:
    status, body = fetch(url)
    if status == 200 and body:
        title = ""
        m = re.search(r'<title>(.*?)</title>', body, re.S)
        if m:
            title = m.group(1).strip()[:80]
        has_book = "What the Green Light Saw" in body
        print(f"{name}: status={status} title={title!r} book_in_body={has_book} len={len(body)}")
    else:
        print(f"{name}: status={status} (body empty/fail)")
