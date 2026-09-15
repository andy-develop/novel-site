#!/usr/bin/env python3
"""Audit chapters dir: word counts, H1 format, forbidden chars, total."""
import os, re, sys

d = sys.argv[1] if len(sys.argv) > 1 else '/root/novels/everyone-lied-about-june/chapters'
files = sorted(f for f in os.listdir(d) if re.fullmatch(r'ch\d{3}\.md', f))
total = 0
issues = []
for f in files:
    p = os.path.join(d, f)
    with open(p, encoding='utf-8') as fh:
        lines = fh.read().split('\n')
    n = int(re.search(r'ch(\d{3})', f).group(1))
    text = '\n'.join(lines)
    words = len(text.split())
    total += words
    h1 = lines[0].strip() if lines else ''
    expect = f'# Chapter {n}:'
    if not h1.startswith(expect):
        issues.append(f'{f}: BAD H1 {h1!r}')
    hashbody = [ln for ln in lines[1:] if ln.strip().startswith('#')]
    if hashbody:
        issues.append(f'{f}: {len(hashbody)} hash-leading body lines')
    if '*' in text:
        issues.append(f'{f}: contains asterisks')
    if '\u2014' in text or '\u2013' in text:
        issues.append(f'{f}: contains em/en dash')
    if '\u201c' in text or '\u201d' in text:
        issues.append(f'{f}: contains curly quotes')
    print(f'{f} {words} {h1}')
print(f'TOTAL_WORDS: {total}')
print(f'CHAPTERS: {len(files)}')
if issues:
    print('--- ISSUES ---')
    for i in issues:
        print(i)
else:
    print('NO FORMAT ISSUES')
