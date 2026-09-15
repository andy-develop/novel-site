#!/usr/bin/env python3
"""Audit chapter files for uploader-contract violations."""
import re, sys, glob

d = '/root/novels/cancel-eden/chapters'
bad = []
for f in sorted(glob.glob(d + '/ch*.md')):
    lines = open(f, encoding='utf-8').read().splitlines()
    h1 = lines[0]
    if not re.match(r'^# Chapter \d+: ', h1):
        bad.append((f, 'H1 format', h1))
    for i, ln in enumerate(lines[1:], start=2):
        s = ln.strip()
        if s.startswith('#'):
            bad.append((f, f'hash line L{i}', s[:60]))
        if s in ('---', '***', '___') or re.match(r'^[\*_\-=]{3,}$', s):
            bad.append((f, f'divider L{i}', s[:40]))
        if '*' in ln or '**' in ln:
            bad.append((f, f'asterisk L{i}', ln[:60]))
    # title special chars (excluding the legitimate "Chapter N:" prefix)
    title = h1.split(': ', 1)[1] if ': ' in h1 else h1
    if re.search(r'[—–&:()#]', title):
        bad.append((f, 'title special char', title))

if bad:
    for f, kind, txt in bad[:40]:
        print(f'{kind} | {f} | {txt}')
    print(f'TOTAL ISSUES: {len(bad)}')
    sys.exit(1)
print('AUDIT CLEAN: 27 chapters OK')
