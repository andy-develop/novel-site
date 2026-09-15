#!/usr/bin/env python3
"""Audit THE DEEP END chapters: H1 format, special chars, hash lines, asterisks, word counts."""
import re, glob, os

d = '/root/novels/the-deep-end/chapters'
files = sorted(glob.glob(os.path.join(d, 'ch*.md')))
print(f"FILES={len(files)}")
problems = []
titles = []
for f in files:
    num = int(re.search(r'ch(\d{3})\.md', f).group(1))
    lines = open(f, encoding='utf-8').read().split('\n')
    h1 = lines[0].strip() if lines else ''
    wc = len(re.findall(r'\S+', open(f, encoding='utf-8').read()))
    # H1 check
    if not re.match(rf'^# Chapter {num}:', h1):
        problems.append(f"{os.path.basename(f)}: BAD H1 {h1!r}")
    title = re.sub(r'^# Chapter \d+: ', '', h1).strip()
    if re.search(r'[—–&:()#*]', title):
        problems.append(f"{os.path.basename(f)}: FORBIDDEN CHARS in title {title!r}")
    if re.search(r'— Day', h1) or re.search(r'Day \d+', title):
        problems.append(f"{os.path.basename(f)}: DAY MARKER in H1 {h1!r}")
    titles.append(title)
    # body checks
    body = lines[1:]
    for i, ln in enumerate(body, 2):
        s = ln.strip()
        if s.startswith('#') and not s.startswith('##'):
            problems.append(f"{os.path.basename(f)}: hash-leading line {i}: {s[:60]}")
        if re.search(r'^\s*(\*\*\*|---|___)\s*$', s):
            problems.append(f"{os.path.basename(f)}: scene divider line {i}")
        if '*' in s:
            problems.append(f"{os.path.basename(f)}: asterisk line {i}: {s[:60]}")
    if wc < 1300:
        problems.append(f"{os.path.basename(f)}: LOW WC {wc}")
    print(f"ch{num:03d} wc={wc} title={title!r}")

print("\n--- TITLES (pattern check) ---")
for t in titles:
    print(" ", t)
the_count = sum(1 for t in titles if t.startswith('The '))
print(f"\nTheX ratio: {the_count}/{len(titles)} = {the_count/len(titles):.0%}")
print(f"\nPROBLEMS ({len(problems)}):")
for p in problems:
    print(" ", p)
