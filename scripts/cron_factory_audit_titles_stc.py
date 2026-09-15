#!/usr/bin/env python3
"""Audit chapters: H1 exactness, special chars in titles, #-leading body lines, asterisks, dividers."""
import os, re, sys

d = '/root/novels/strip-the-coat/chapters'
issues = []
titles = []
for f in sorted(os.listdir(d)):
    if not re.fullmatch(r'ch\d{3}\.md', f):
        issues.append(f'{f}: BAD FILENAME')
        continue
    n = int(re.search(r'ch(\d{3})', f).group(1))
    lines = open(os.path.join(d, f), encoding='utf-8').read().splitlines()
    if not lines[0].startswith(f'# Chapter {n}:'):
        issues.append(f'{f}: H1 wrong: {lines[0]!r}')
    h1 = lines[0][2:].strip()
    titles.append(h1)
    # title special chars
    bad = re.findall(r'[#—–&:()]', h1)
    if bad:
        issues.append(f'{f}: TITLE SPECIAL CHARS {bad}: {h1}')
    # body checks
    for i, ln in enumerate(lines[1:], 2):
        if ln.startswith('#'):
            issues.append(f'{f}:{i}: hash-leading line: {ln[:60]!r}')
        if re.search(r'\*\*', ln):
            issues.append(f'{f}:{i}: asterisks: {ln[:60]!r}')
        if ln.strip() == '---':
            issues.append(f'{f}:{i}: divider')
        if ln.startswith('- ') or re.match(r'^\d+\.\s', ln):
            issues.append(f'{f}:{i}: list-like line: {ln[:60]!r}')
# title pattern audit
the_start = sum(1 for t in titles if t.startswith('The '))
print('CHAPTERS', len(titles))
print('The-start', the_start, f'({the_start/len(titles)*100:.1f}%)')
for t in titles:
    print(' T:', t)
print('ISSUES:', len(issues))
for i in issues:
    print(' !', i)
