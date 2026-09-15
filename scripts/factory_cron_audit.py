#!/usr/bin/env python3
"""Audit chapters dir: file names, H1, word counts, banned chars, artifacts."""
import os, re, sys

d = "/root/novels/ice-out/chapters"
files = sorted(f for f in os.listdir(d) if re.fullmatch(r"ch\d{3}\.md", f))
print(f"chapter files: {len(files)}")
total = 0
problems = []
for f in files:
    p = os.path.join(d, f)
    n = int(re.match(r"ch(\d{3})\.md", f).group(1))
    txt = open(p, encoding="utf-8").read()
    lines = txt.split("\n")
    h1 = lines[0].strip()
    words = len(txt.split())
    total += words
    issues = []
    # H1 check
    if not re.match(rf"^# Chapter {n}: .+", h1):
        issues.append(f"H1_BAD: {h1!r}")
    # banned chars in H1 title part (after "# Chapter N: " prefix)
    title_part = re.sub(r"^# Chapter \d+: ", "", h1)
    for ch in "#—–&:()":
        if ch in title_part:
            issues.append(f"H1_BANNED_CHAR {ch!r}")
    # body lines starting with #
    body_hashes = [l for l in lines[1:] if l.strip().startswith("#")]
    if body_hashes:
        issues.append(f"BODY_HASH x{len(body_hashes)}")
    # asterisks / markdown
    if re.search(r"\*\*|\*|__|~~|^---$|^====", txt, re.M):
        issues.append("MARKDOWN_ARTIFACT")
    # word floor
    if words < 1300:
        issues.append(f"LOW_WORDS {words}")
    if issues:
        problems.append((f, issues))
    print(f"{f}: {words:6d}w  H1={h1[:60]}")
print(f"TOTAL: {total} words")
if problems:
    print("\nPROBLEMS:")
    for f, iss in problems:
        print(f, iss)
else:
    print("\nNO PROBLEMS")
