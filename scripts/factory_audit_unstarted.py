#!/usr/bin/env python3
"""Audit chapters: H1 vs brief titles, bad lines, word counts, title chars."""
import re, os, sys

ch_dir = '/root/novels/unstarted/chapters'
brief = open('/root/novels/unstarted/outlines/brief-unstarted.md', encoding='utf-8').read()

# expected titles from brief: lines like "### Ch1 — \"The Pending Girl\" (Fri Oct 2)"
expected = {}
for m in re.finditer(r'### Ch(\d+) — "([^"]+)"', brief):
    expected[int(m.group(1))] = m.group(2)

problems = []
tot = 0
min_w = 999999
for n in range(1, 31):
    f = os.path.join(ch_dir, f'ch{n:03d}.md')
    text = open(f, encoding='utf-8').read()
    lines = text.split('\n')
    h1 = lines[0] if lines else ''
    wc = len(text.split())
    tot += wc
    min_w = min(min_w, wc)
    # H1 check
    want = f'# Chapter {n}: {expected.get(n, "?")}'
    if h1.strip() != want:
        problems.append(f'ch{n:03d} H1: got "{h1.strip()[:60]}" want "{want[:60]}"')
    # bad lines
    for i, ln in enumerate(lines[1:], 2):
        s = ln.strip()
        if s.startswith('#'):
            problems.append(f'ch{n:03d} line {i}: hash-leading "{s[:40]}"')
        if '*' in s or '—' in s or '–' in s:
            problems.append(f'ch{n:03d} line {i}: special char in "{s[:40]}"')
    # title chars
    t = expected.get(n, '')
    for ch in '#—–&:()':
        if ch in t:
            problems.append(f'ch{n:03d} TITLE has banned char "{ch}"')
    if wc < 1300:
        problems.append(f'ch{n:03d} TOO SHORT: {wc}')

print(f'total_words={tot} min_chapter_words={min_w} chapters=30')
the_count = sum(1 for t in expected.values() if t.startswith('The '))
print(f'titles_starting_The={the_count}/30')
if problems:
    print('PROBLEMS:')
    for p in problems:
        print(' -', p)
else:
    print('NO PROBLEMS')
