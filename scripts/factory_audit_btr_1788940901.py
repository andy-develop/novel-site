#!/usr/bin/env python3
"""Audit chapters: H1 contract, special chars, The-count, totals. Read-only."""
import re, glob, os

d = "/root/novels/better-to-reign/chapters"
files = sorted(glob.glob(os.path.join(d, "ch*.md")))
print(f"FILES: {len(files)}")
total = 0
h1s = []
problems = []
for f in files:
    name = os.path.basename(f)
    if not re.fullmatch(r"ch\d{3}\.md", name):
        problems.append(f"BAD FILENAME: {name}")
    lines = open(f, encoding="utf-8").read().splitlines()
    wc = sum(len(l.split()) for l in lines)
    total += wc
    h1 = None
    for i, l in enumerate(lines):
        if l.startswith("#"):
            h1 = l
            break
    if h1 is None:
        problems.append(f"{name}: NO H1")
        h1s.append(("MISSING", ""))
        continue
    # H1 must be line 1
    if not lines[0].startswith("# Chapter "):
        problems.append(f"{name}: H1 NOT LINE 1 -> {h1[:60]!r}")
    m = re.match(r"^# Chapter (\d+): (.+)$", h1)
    if not m:
        problems.append(f"{name}: H1 FORMAT -> {h1[:80]!r}")
        h1s.append((name, h1))
        continue
    num = int(m.group(1))
    title = m.group(2)
    if num != int(name[2:5]):
        problems.append(f"{name}: H1 NUMBER {num} != filename")
    if re.search(r"[#—–&:()]", title):
        problems.append(f"{name}: SPECIAL CHAR IN TITLE -> {title!r}")
    if title.strip() != title or "  " in title:
        problems.append(f"{name}: title whitespace -> {title!r}")
    h1s.append((name, title))
    # body lines starting with # (after H1)
    for i, l in enumerate(lines[1:], 2):
        if l.startswith("#"):
            problems.append(f"{name}: hash line {i} -> {l[:60]!r}")
    # asterisks in body
    for i, l in enumerate(lines[1:], 2):
        if "*" in l:
            problems.append(f"{name}: asterisk line {i} -> {l[:60]!r}")

print(f"TOTAL_WORDS: {total}")
the = [t for _, t in h1s if t.startswith("The ")]
print(f"THE_COUNT: {len(the)}/30 = {100*len(the)//30}%")
print("TITLES:")
for name, t in h1s:
    print(f"  {name}: {t}")
if problems:
    print("PROBLEMS:")
    for p in problems:
        print("  ", p)
else:
    print("NO PROBLEMS")
