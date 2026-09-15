#!/usr/bin/env python3
"""Audit chapter files: H1 format, forbidden chars, hash lines, word counts, title patterns."""
import os, re, glob

d = '/root/novels/the-frog-ledger/chapters'
files = sorted(glob.glob(os.path.join(d, 'ch*.md')))
print(f"files={len(files)}")

the_count = 0
patterns = {}
for f in files:
    num = int(re.search(r'ch(\d+)\.md', f).group(1))
    lines = open(f, encoding='utf-8').read().split('\n')
    h1 = lines[0].strip()
    words = sum(len(l.split()) for l in lines)
    ok = True
    # H1 checks
    if not h1.startswith(f'# Chapter {num}:'):
        print(f"!! {os.path.basename(f)} H1 prefix wrong: {h1!r}"); ok = False
    title = h1.replace(f'# Chapter {num}:', '').strip()
    if re.search(r'[#—–&:()]', title):
        print(f"!! {os.path.basename(f)} title has forbidden chars: {title!r}"); ok = False
    if title.endswith('.'):
        print(f"!! {os.path.basename(f)} title ends with period: {title!r}"); ok = False
    if re.search(r'—|–', h1):
        print(f"!! {os.path.basename(f)} H1 has em/en dash: {h1!r}"); ok = False
    if 'Day' in title:
        print(f"!! {os.path.basename(f)} H1 contains Day marker: {title!r}"); ok = False
    if title.startswith('The '):
        the_count += 1
    # first word pattern for variety
    first = title.split()[0].lower() if title.split() else ''
    patterns.setdefault(first, []).append(num)
    # body checks
    for i, l in enumerate(lines[1:], 2):
        s = l.strip()
        if s.startswith('#'):
            print(f"!! {os.path.basename(f)} line {i} starts with #: {s[:50]!r}"); ok = False
        if re.search(r'\*\*|\*[^*]+\*', s) and '*' in s:
            print(f"!! {os.path.basename(f)} line {i} has asterisks: {s[:60]!r}"); ok = False
    if words < 1300:
        print(f"!! {os.path.basename(f)} THIN: {words} words"); ok = False
    if ok:
        pass
    # per-file word count one-liner
    print(f"ch{num:03d} {words:5d} | {title}")

print(f"\n'The X' opener count: {the_count}/{len(files)} = {100*the_count/len(files):.0f}%")
print(f"distinct first-words (patterns): {len(patterns)}")
for w, nums in sorted(patterns.items(), key=lambda x: -len(x[1])):
    print(f"  {w!r}: {len(nums)}x chapters {nums}")
