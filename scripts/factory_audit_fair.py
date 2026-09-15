#!/usr/bin/env python3
"""Audit chapters for upload contract: H1 format, forbidden chars, The-ratio, thin chapters, word totals."""
import os, re, sys

d = sys.argv[1] if len(sys.argv) > 1 else '/root/novels/she-plays-the-fair/chapters'
files = sorted(f for f in os.listdir(d) if re.fullmatch(r'ch\d{3}\.md', f))
total = 0
the_cnt = 0
issues = []
nums = []
for f in files:
    n = int(re.search(r'ch(\d{3})', f).group(1))
    nums.append(n)
    text = open(os.path.join(d, f), encoding='utf-8').read()
    lines = text.split('\n')
    h1 = lines[0].strip()
    if not re.match(rf'^# Chapter {n}: .+', h1):
        issues.append(f"{f}: BAD H1 {h1!r}")
    title = h1[2:].strip() if h1.startswith('# ') else h1
    m = re.match(r'^Chapter \d+:\s*(.+)$', title)
    if m:
        title = m.group(1).strip()
    if re.search(r'[#—–&:()]', title):
        issues.append(f"{f}: FORBIDDEN CHAR in title {title!r}")
    if title.startswith('The '):
        the_cnt += 1
    for i, ln in enumerate(lines[1:], 2):
        if ln.startswith('#'):
            issues.append(f"{f}: hash-leading line {i}: {ln[:40]!r}")
    words = len(text.split())
    total += words
    if words < 1300:
        issues.append(f"{f}: THIN {words} words")
    print(f"{f}: {words}w  {title[:55]}")
print(f"TOTAL {total} words, {len(files)} files")
print(f"The-openers: {the_cnt}/{len(files)} = {100.0*the_cnt/len(files):.0f}%")
if nums:
    expect = list(range(min(nums), max(nums) + 1))
    if nums != expect:
        issues.append(f"NON-CONTIGUOUS: {nums}")
print("ISSUES:" if issues else "NO ISSUES")
for i in issues:
    print(" -", i)
