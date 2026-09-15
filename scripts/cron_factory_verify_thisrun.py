#!/usr/bin/env python3
"""Live-site verification for cron factory book: retry loop, Chrome UA."""
import subprocess, time, sys, json

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

def curl(url, tries=6, timeout=25):
    last = None
    for i in range(tries):
        try:
            r = subprocess.run(
                ["curl", "-s", "-o", "/tmp/vf_body.html", "-w", "%{http_code}", "-A", UA,
                 "-L", "--max-time", str(timeout), url],
                capture_output=True, text=True, timeout=timeout + 10)
            code = r.stdout.strip()
            if code == "200":
                return code, open("/tmp/vf_body.html", encoding="utf-8", errors="replace").read()
            last = code
        except Exception as e:
            last = f"ERR:{e}"
        time.sleep(4)
    return last, ""

checks = [
    ("ch1", "https://lyriq.top/novel/draft-saved/1"),
    ("ch30", "https://lyriq.top/novel/draft-saved/30"),
    ("home", "https://lyriq.top/"),
    ("bogus", "https://lyriq.top/novel/definitely-not-a-real-slug-zzz/1"),
]
for name, url in checks:
    code, body = curl(url)
    print(f"{name}: HTTP {code}", flush=True)
    if code == "200" and body:
        if name == "ch1":
            import re
            m = re.search(r"<title>(.*?)</title>", body, re.S)
            print("  TITLE:", m.group(1).strip()[:100] if m else "NONE")
            print("  BOOKID_1547_PRESENT:", ("1547" in body))
        if name == "ch30":
            import re
            m = re.search(r"<title>(.*?)</title>", body, re.S)
            print("  TITLE:", m.group(1).strip()[:100] if m else "NONE")
        if name == "home":
            print("  CONTAINS_DRAFT_SAVED:", ("Draft Saved" in body))
        if name == "bogus":
            print("  IS_404:", ("404" in body or "not found" in body.lower() or code != "200"))
