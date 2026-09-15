#!/usr/bin/env python3
"""Verify live site pages for the-good-man. Retries for SSR 1102 flakiness."""
import re, subprocess, sys, time

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

def fetch(url, retries=6):
    for i in range(retries):
        r = subprocess.run(
            ["curl", "-s", "-o", "/tmp/vpage.html", "-w", "%{http_code}", "-A", UA, "-L", url],
            capture_output=True, text=True, timeout=60)
        code = r.stdout.strip()
        if code == "200":
            body = open("/tmp/vpage.html", encoding="utf-8", errors="replace").read()
            return code, body
        time.sleep(4)
    return code, ""

ok = True
# 1. Chapter 1 page
code, body = fetch("https://lyriq.top/novel/the-good-man/1")
t1 = re.search(r"<title>([^<]*)</title>", body or "")
print(f"ch1 page: {code} title={t1.group(1) if t1 else 'NONE'}")
if code != "200" or not t1 or "Case File One" not in t1.group(1):
    ok = False

# 2. Last chapter page
code, body = fetch("https://lyriq.top/novel/the-good-man/30")
t2 = re.search(r"<title>([^<]*)</title>", body or "")
print(f"ch30 page: {code} title={t2.group(1) if t2 else 'NONE'}")
if code != "200" or not t2 or "Aftermath" not in t2.group(1):
    ok = False

# 3. Home page contains title
code, body = fetch("https://lyriq.top/")
print(f"home: {code} contains_title={'The Good Man' in (body or '')}")
if code != "200" or "The Good Man" not in (body or ""):
    ok = False

# 4. Bogus slug -> 404
code, _ = fetch("https://lyriq.top/novel/definitely-not-a-real-slug-xyz/1")
print(f"bogus slug: {code}")
if code != "404":
    ok = False

print("VERIFY:", "PASS" if ok else "FAIL")
