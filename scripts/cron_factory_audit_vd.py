#!/usr/bin/env python3
"""Audit chapters dir: word counts, H1 contract, forbidden chars, body # lines."""
import os, re, sys

d = '/root/novels/viral-descent/chapters'
files = sorted(f for f in os.listdir(d) if re.fullmatch(r'ch\d{3}\.md', f))
total = 0
problems = []
for f in files:
    path = os.path.join(d, f)
    lines = open(path, encoding='utf-8').read().split('\n')
    n = int(re.search(r'ch(\d{3})\.md', f).group(1))
    # words
    wc = len(open(path, encoding='utf-8').read().split())
    total += wc
    flag = ''
    if wc < 1800:
        flag = ' <== UNDER 1800'
        problems.append(f'{f}: {wc} words under floor')
    # H1
    h1 = lines[0] if lines else ''
    if not h1.startswith(f'# Chapter {n}:'):
        problems.append(f'{f}: H1 mismatch: {h1!r}')
    if '—' in h1 or '–' in h1:
        problems.append(f'{f}: em/en dash in H1: {h1!r}')
    for bad in ['#', '&', ':', '(', ')']:
        t = re.sub(r'^Chapter \d+:\s*', '', h1[2:])
        if bad in t:
            problems.append(f'{f}: forbidden char {bad!r} in title: {t!r}')
    # body lines starting with # (skip H1)
    for i, ln in enumerate(lines[1:], 2):
        if ln.startswith('#'):
            problems.append(f'{f}: line {i} starts with #: {ln[:60]!r}')
    # asterisks anywhere in body
    body = '\n'.join(lines[1:])
    if '*' in body:
        problems.append(f'{f}: asterisk found in body')
    # scene dividers
    if re.search(r'^\s*(\*\*\*|---|___)\s*$', body, re.M):
        problems.append(f'{f}: scene divider found')
    print(f'{wc:5d} {f}{flag}')
print(f'TOTAL: {total} words, {len(files)} files')
if problems:
    print('\nPROBLEMS:')
    for p in problems:
        print(' -', p)
    sys.exit(1)
print('AUDIT OK')
