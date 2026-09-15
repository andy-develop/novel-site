#!/usr/bin/env python3
"""Factory audit: per-chapter words, hash-lines, asterisks, title chars, thin chapters."""
import re, sys, os

d = '/root/novels/the-rabbit-farm/chapters'
files = sorted(f for f in os.listdir(d) if re.fullmatch(r'ch\d{3}\.md', f))
total = 0
problems = []
the_count = 0
for f in files:
    n = int(re.search(r'ch(\d{3})', f).group(1))
    lines = open(os.path.join(d, f), encoding='utf-8').read().split('\n')
    h1 = lines[0]
    body = '\n'.join(lines[1:])
    words = len(body.split())
    total += words
    if words < 1300:
        problems.append(f"{f}: THIN {words}w")
    if not h1.startswith(f'# Chapter {n}:'):
        problems.append(f"{f}: H1 mismatch {h1!r}")
    title = re.sub(r'^Chapter \d+:\s*', '', h1[2:].strip())
    if re.search(r'[#—–&:()]', title):
        problems.append(f"{f}: title special chars {title!r}")
    if title.startswith('The '):
        the_count += 1
    # body checks
    for i, ln in enumerate(lines[1:], 2):
        s = ln.strip()
        if s.startswith('#'):
            problems.append(f"{f}:{i} hash-leading line: {s[:60]!r}")
        if re.search(r'\*\*|^\*|\*$|~~~|```|^---$', s):
            problems.append(f"{f}:{i} markdown artifact: {s[:60]!r}")
print(f"files={len(files)} total_words={total}")
print(f"The-openers: {the_count}/{len(files)} = {100*the_count/len(files):.0f}%")
if problems:
    print("PROBLEMS:")
    for p in problems:
        print(" ", p)
else:
    print("NO FORMAT PROBLEMS")
