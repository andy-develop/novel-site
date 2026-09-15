#!/usr/bin/env python3
"""Audit chapters dir: word counts, H1 format, forbidden chars, bad lines."""
import os, re, sys

d = sys.argv[1] if len(sys.argv) > 1 else '/root/novels/the-mill-audit/chapters'
files = sorted(f for f in os.listdir(d) if re.fullmatch(r'ch\d{3}\.md', f))
total = 0
print(f"{'file':8} {'words':>6}  H1")
for f in files:
    lines = open(os.path.join(d, f), encoding='utf-8').read().splitlines()
    # word count excluding the H1 line
    body = [l for l in lines if not l.startswith('#')]
    wc = sum(len(l.split()) for l in body)
    total += wc
    h1 = lines[0] if lines else '(EMPTY)'
    flag = ''
    if not h1.startswith('# Chapter '):
        flag = '  !! BAD H1'
    else:
        title_part = h1.split(':', 1)[1] if ':' in h1 else h1
        if re.search(r'[—–&:()]', title_part):
            flag = '  !! SPECIAL CHAR IN TITLE'
        elif title_part.rstrip().endswith('.'):
            flag = '  !! TRAILING PERIOD'
    if ' Day ' in h1:
        flag += '  !! DAY MARKER'
    print(f"{f:8} {wc:6d}  {h1[:70]}{flag}")
    # check body for forbidden markdown
    bad = []
    for i, l in enumerate(lines):
        if l.startswith('#') and i > 0:
            bad.append(f"hash-line@{i}")
        if re.match(r'^\s*(\*\*\*|---|___)\s*$', l):
            bad.append(f"divider@{i}")
        if '*' in l or '**' in l:
            bad.append(f"asterisk@{i}")
    if bad:
        print(f"         !! {bad[:6]}")
print(f"TOTAL: {total} words across {len(files)} files")
