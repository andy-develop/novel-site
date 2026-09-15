#!/usr/bin/env python3
"""Verify citizen-zero on lyriq.top with Chrome UA + retries (site 503s ~50% under CPU pressure)."""
import subprocess, time

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

def fetch(url, tries=8):
    for i in range(tries):
        r = subprocess.run(["curl", "-s", "-o", "/tmp/vz_body.html", "-w", "%{http_code}",
                            "-A", UA, "--max-time", "30", url], capture_output=True, text=True)
        code = r.stdout.strip()
        if code == "200":
            body = open("/tmp/vz_body.html", encoding="utf-8", errors="replace").read()
            return code, body
        time.sleep(3)
    return code, ""

c1, b1 = fetch("https://lyriq.top/novel/citizen-zero/1")
print("ch1:", c1)
if c1 == "200":
    import re
    m = re.search(r"<title>(.*?)</title>", b1, re.S)
    print("title:", (m.group(1).strip() if m else "NONE"))
    print("has_chapter1_h1:", "Fired Before Noon" in b1)

c30, _ = fetch("https://lyriq.top/novel/citizen-zero/30")
print("ch30:", c30)

ch, bh = fetch("https://lyriq.top/")
print("home:", ch)
if ch == "200":
    print("home_has_title:", "CITIZEN ZERO" in bh)

cb, _ = fetch("https://lyriq.top/novel/citizen-zero/no-such-book-xyz")
print("bogus_slug:", cb)
