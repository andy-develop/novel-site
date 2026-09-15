#!/usr/bin/env python3
"""Find which home page(s) list UNREADABLE; check bogus-slug redirect target."""
import subprocess, re, time

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

def fetch(url, tries=6):
    for i in range(tries):
        r = subprocess.run(["curl", "-s", "-o", "/tmp/p.html", "-w", "%{http_code}", "-A", UA,
                            "--max-time", "25", url], capture_output=True, text=True)
        code = r.stdout.strip()
        body = open("/tmp/p.html", encoding="utf-8", errors="replace").read()
        if code == "200" and body.strip():
            return code, body
        time.sleep(3)
    return code, ""

# 1. check redirect target of bogus slug
r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code} %{redirect_url}", "-A", UA,
                    "--max-time", "25", "https://lyriq.top/novel/this-slug-does-not-exist-xyz/1"],
                   capture_output=True, text=True)
print("bogus:", r.stdout.strip())

# 2. home page structure: look for pagination hints + how books are sorted
code, body = fetch("https://lyriq.top/")
# find links to /novel/ slugs on this page
links = set(re.findall(r'/novel/([a-z0-9-]+)/', body))
print(f"home page1: {len(links)} distinct book links")
print("sample:", sorted(links)[:12])

# does the page carry a 'page' param or total count?
m = re.findall(r'href="[^"]*\?page=(\d+)"', body)
print("pagination links on page1:", sorted(set(int(x) for x in m))[:10])

# 3. try page 2, 3 ... find unreadable; also try the tag/dystopia page
for pg in range(1, 6):
    code, body = fetch(f"https://lyriq.top/?page={pg}" if pg > 1 else "https://lyriq.top/")
    if "unreadable" in body.lower():
        print(f"FOUND 'unreadable' on home page {pg}")
        break
    else:
        print(f"page {pg}: not found ({len(body)} chars)")
