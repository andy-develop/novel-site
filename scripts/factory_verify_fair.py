#!/usr/bin/env python3
"""Phase 7 live-site verification via curl with Chrome UA."""
import subprocess, sys, re

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

def curl(url, tries=5):
    for i in range(tries):
        try:
            r = subprocess.run(["curl", "-s", "-o", "/tmp/lyrq.html", "-w", "%{http_code}", "-A", UA, "--max-time", "25", url],
                               capture_output=True, text=True, timeout=40)
            code = r.stdout.strip()
            if code in ("200", "404"):
                return code
        except Exception:
            pass
        time_sleep(4)
    return "FAIL"

def time_sleep(n):
    import time
    time.sleep(n)

def title():
    try:
        return re.search(r"<title>(.*?)</title>", open("/tmp/lyrq.html", encoding="utf-8", errors="ignore").read(), re.S).group(1).strip()[:80]
    except Exception:
        return "?"

slug = sys.argv[1]
last = sys.argv[2]
base = "https://lyriq.top"
c1 = curl(f"{base}/novel/{slug}/1")
t1 = title()
c2 = curl(f"{base}/novel/{slug}/{last}")
t2 = title()
ch = curl(f"{base}/")
t3 = title()
c4 = curl(f"{base}/novel/definitely-not-a-real-slug-xyz")
print(f"ch1:  {c1} <title>{t1}</title>")
print(f"ch{last}: {c2} <title>{t2}</title>")
print(f"home: {ch} <title>{t3}</title>")
print(f"bogus: {c4} (expect 404)")
