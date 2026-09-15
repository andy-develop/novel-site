#!/usr/bin/env python3
"""Factory audit: word counts, H1 format, banned chars in titles, hash-leading lines, chapter gaps."""
import glob, os, re, sys

d = sys.argv[1] if len(sys.argv) > 1 else "/root/novels/enemy-of-the-feed"
chdir = os.path.join(d, "chapters")
files = sorted(glob.glob(os.path.join(chdir, "ch*.md")))
print(f"files: {len(files)}")
nums = []
total = 0
issues = []
for f in files:
    name = os.path.basename(f)
    m = re.fullmatch(r"ch(\d{3})\.md", name)
    if not m:
        issues.append(f"BAD FILENAME {name}")
        continue
    n = int(m.group(1))
    nums.append(n)
    lines = open(f, encoding="utf-8").read().splitlines()
    words = len(open(f, encoding="utf-8").read().split())
    total += words
    h1 = lines[0] if lines else ""
    t = h1.replace("# ", "", 1)
    ok_h1 = re.fullmatch(r"# Chapter \d+: .+", h1)
    if not ok_h1:
        issues.append(f"{name} BAD H1: {h1[:60]!r}")
    elif re.search(r"[—–]|&|\u2014", h1):
        issues.append(f"{name} H1 SPECIAL CHAR: {h1}")
    elif re.search(r"[—–:()]", re.sub(r"^Chapter \d+: ", "", t)):
        issues.append(f"{name} TITLE SPECIAL CHAR: {t}")
    if ok_h1 and not t.startswith(f"Chapter {n}:"):
        issues.append(f"{name} H1 NUM MISMATCH (file {n}): {t[:50]}")
    if words < 1300:
        issues.append(f"{name} THIN {words}w")
    for i, ln in enumerate(lines[1:], 2):
        if ln.startswith("#"):
            issues.append(f"{name} hash-leading line {i}: {ln[:50]!r}")
            break
        if ln.strip() in ("---", "***", "~~~") or re.fullmatch(r"[-*_]{3,}", ln.strip()):
            issues.append(f"{name} scene divider line {i}")
            break
missing = [n for n in range(1, max(nums) + 1) if n not in nums]
if missing:
    issues.append(f"MISSING CHAPTERS: {missing}")
print(f"chapters: {min(nums)}..{max(nums)}  total_words: {total}  avg: {total//len(nums)}")
if issues:
    print("ISSUES:")
    for i in issues:
        print(" -", i)
else:
    print("ISSUES: none")
