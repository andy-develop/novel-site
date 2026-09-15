#!/usr/bin/env python3
"""Read-only format audit for SAINTFALL chapters."""
import re, glob, sys

files = sorted(glob.glob('/root/novels/saintfall/chapters/ch*.md'))
print(f"files: {len(files)}")
issues = []
for f in files:
    n = f.split('/')[-1]
    if not re.fullmatch(r'ch\d{3}\.md', n):
        issues.append(f"{n}: BAD FILENAME")
    with open(f, encoding='utf-8') as fh:
        lines = fh.read().split('\n')
    # H1 check
    if not lines or not re.match(r'^# Chapter \d+: .+', lines[0]):
        issues.append(f"{n}: bad H1: {lines[0][:50]!r}")
    # no other hash lines
    for i, ln in enumerate(lines[1:], start=2):
        if ln.startswith('#'):
            issues.append(f"{n}: hash line {i}: {ln[:60]!r}")
        if re.match(r'^\s*(\*\*\*|---|___)\s*$', ln):
            issues.append(f"{n}: scene divider line {i}")
        if '*' in ln or '_' in ln and '**' in ln:
            pass
        if '**' in ln:
            issues.append(f"{n}: bold/italic line {i}: {ln[:60]!r}")
    # special chars in H1 title (after 'Chapter N: ')
    m = re.match(r'^# Chapter \d+: (.+)$', lines[0])
    if m:
        t = m.group(1)
        if re.search(r'[#—–&:()]', t):
            issues.append(f"{n}: special char in title: {t!r}")
        if t.startswith('The '):
            pass  # count later
    # paragraph length (lines over 6 lines of text = >~90 words per para? approximate by char)
    for i, ln in enumerate(lines, start=1):
        if len(ln) > 700:
            issues.append(f"{n}: very long para line {i} ({len(ln)} chars)")
print("issues:")
for x in issues:
    print(" -", x)
print("done" if not issues else f"{len(issues)} issues")
