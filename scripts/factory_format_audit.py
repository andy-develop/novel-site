#!/usr/bin/env python3
"""Audit chapter format: H1, titles, forbidden chars, markdown leakage, word counts."""
import re, os, glob

d = '/root/novels/delete-him/chapters'
files = sorted(glob.glob(os.path.join(d, 'ch*.md')))
print(f"FILES={len(files)}")
problems = []
titles = []
total = 0
for f in files:
    n = os.path.basename(f)
    with open(f, encoding='utf-8') as fh:
        lines = fh.read().split('\n')
    # strip leading blanks
    while lines and not lines[0].strip():
        lines.pop(0)
    h1 = lines[0] if lines else ''
    m = re.match(r'^# Chapter (\d+): (.+)$', h1)
    if not m:
        problems.append(f"{n}: BAD H1: {h1!r}")
        continue
    num, title = int(m.group(1)), m.group(2).strip()
    expect = f'ch{num:03d}.md'
    if expect != n:
        problems.append(f"{n}: number mismatch with filename ({expect})")
    titles.append((num, title))
    # forbidden chars in title
    if re.search(r'[#—–&:()]', title):
        problems.append(f"{n}: FORBIDDEN CHAR in title: {title!r}")
    # body: no lines starting with #, no asterisks, no --- dividers
    body = lines[1:]
    for i, ln in enumerate(body, start=2):
        s = ln.strip()
        if s.startswith('#'):
            problems.append(f"{n}: line {i} starts with #: {s[:40]!r}")
        if '*' in s and not s.startswith('*'):
            problems.append(f"{n}: line {i} contains asterisk: {s[:40]!r}")
        if re.match(r'^-{3,}$', s) or re.match(r'^\*{3,}$', s):
            problems.append(f"{n}: line {i} scene divider: {s[:20]!r}")
    wc = len(' '.join(body).split())
    total += wc
    if wc < 1300:
        problems.append(f"{n}: LOW WORDS {wc}")
# title pattern check
the_count = sum(1 for _, t in titles if t.startswith('The '))
print(f"TOTAL_WORDS={total}")
print(f"THE_STARTERS={the_count}/{len(titles)} = {100*the_count//max(1,len(titles))}%")
print("TITLES:")
for num, t in titles:
    print(f"  ch{num:03d}: {t}")
if problems:
    print("PROBLEMS:")
    for p in problems:
        print("  ", p)
else:
    print("NO FORMAT PROBLEMS")
