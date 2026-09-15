#!/usr/bin/env python3
"""Format audit for chapter dir: hash-leading lines, asterisks, scene dividers, H1 sanity."""
import os, re, sys

d = sys.argv[1] if len(sys.argv) > 1 else '/root/novels/where-the-smoke-went/chapters'
files = sorted(f for f in os.listdir(d) if re.fullmatch(r'ch\d{3}\.md', f))
print('files:', len(files))
issues = []
for f in files:
    path = os.path.join(d, f)
    lines = open(path, encoding='utf-8').read().split('\n')
    h1 = lines[0].strip() if lines else ''
    if not re.match(r'^# Chapter \d+: ', h1):
        issues.append(f'{f}: BAD H1 {h1!r}')
    # first line must be H1; check no second H1
    for i, ln in enumerate(lines[1:], start=2):
        s = ln.strip()
        if s.startswith('#'):
            issues.append(f'{f}:{i}: hash-leading line {s[:60]!r}')
        if re.match(r'^\*{3,}\s*$', s) or re.match(r'^-{3,}\s*$', s):
            issues.append(f'{f}:{i}: scene divider {s[:20]!r}')
        if '*' in s:
            issues.append(f'{f}:{i}: asterisk in body: {s[:60]!r}')
print('issues:', len(issues))
for i in issues[:60]:
    print(' ', i)
# em dash in H1?
for f in files:
    h1 = open(os.path.join(d, f), encoding='utf-8').readline()
    if '—' in h1 or '–' in h1:
        print('EMDASH H1:', f, h1.strip())
