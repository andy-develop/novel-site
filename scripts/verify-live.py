#!/usr/bin/env python3
"""Verify live site pages for the new book. Retries for intermittent SSR 503s."""
import subprocess, sys, time, re

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

def fetch(url, tries=8):
    last = None
    for i in range(tries):
        r = subprocess.run(
            ["curl", "-s", "-o", "/tmp/page.html", "-w", "%{http_code}", "-A", UA,
             "--max-time", "25", url],
            capture_output=True, text=True)
        code = r.stdout.strip()
        try:
            body = open("/tmp/page.html", encoding="utf-8", errors="replace").read()
        except Exception:
            body = ""
        if code == "200" and body.strip():
            return code, body
        last = (code, len(body))
        time.sleep(3)
    return last[0], ""

urls = [
    ("ch1", "https://lyriq.top/novel/unreadable/1"),
    ("last", "https://lyriq.top/novel/unreadable/32"),
    ("home", "https://lyriq.top/"),
    ("bogus", "https://lyriq.top/novel/this-slug-does-not-exist-xyz/1"),
]

for name, url in urls:
    code, body = fetch(url)
    print(f"{name}: {url} -> HTTP {code}, body {len(body)} chars")
    if code == "200":
        # title tag
        m = re.search(r"<title>(.*?)</title>", body, re.S)
        print(f"  title: {(m.group(1).strip()[:120] if m else 'NONE')}")
        low = body.lower()
        if "unreadable" in low:
            print("  contains 'unreadable' ✓")
        else:
            print("  !! 'unreadable' NOT in page")
        if name == "ch1":
            m2 = re.search(r"Chapter 1[: ]", body)
            print(f"  Chapter-1 ref: {'✓' if m2 else '?? not found'}")
    print()
