#!/usr/bin/env python3
"""Audit a novel chapters dir: H1 format, word counts, forbidden title chars,
hash-leading body lines, 'The X' ratio. Usage: python3 audit-chapters.py <dir>"""
import os, re, sys

d = sys.argv[1]
files = sorted(f for f in os.listdir(os.path.join(d, "chapters")) if re.fullmatch(r'ch\d{3}\.md', f))
total = 0
the_count = 0
issues = []
print(f"{'file':8s} {'words':>6s}  title")
for f in files:
    path = os.path.join(d, "chapters", f)
    lines = open(path, encoding='utf-8').read().split('\n')
    h1 = next((l for l in lines if l.startswith('# ')), None)
    body = [l for l in lines if l.strip() and not l.startswith('#')]
    words = sum(len(l.split()) for l in body)
    total += words
    if h1 is None:
        issues.append(f"{f}: NO H1")
        continue
    m = re.match(r'# Chapter (\d+): (.+)', h1)
    if not m:
        issues.append(f"{f}: bad H1 {h1!r}")
        continue
    num, title = int(m.group(1)), m.group(2)
    if num != int(f[2:5]):
        issues.append(f"{f}: H1 number {num} != filename")
    if re.search(r'[—–&:()#]', title):
        issues.append(f"{f}: forbidden char in title {title!r}")
    if title.startswith("The "):
        the_count += 1
    print(f"{f:8s} {words:6d}  {title}")
    # hash-leading body lines
    for l in lines[1:]:
        if l.startswith('#'):
            issues.append(f"{f}: hash-leading body line {l[:60]!r}")
print(f"\nTOTAL WORDS: {total}  (target >= 50000)")
print(f"chapters: {len(files)}  'The X' titles: {the_count} ({100*the_count/len(files):.0f}%, limit 30%)")
if issues:
    print("\nISSUES:")
    for i in issues:
        print(" -", i)
else:
    print("NO ISSUES")
