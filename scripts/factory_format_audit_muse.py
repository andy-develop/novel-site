#!/usr/bin/env python3
"""Audit chapter files: H1 format, numbering, title chars, The-count."""
import re, os

d = '/root/novels/muse-no-more/chapters'
files = sorted(f for f in os.listdir(d) if re.fullmatch(r'ch\d{3}\.md', f))
bad = []
the_count = 0
for f in files:
    num = int(re.search(r'ch(\d{3})\.md', f).group(1))
    lines = open(os.path.join(d, f), encoding='utf-8').read().splitlines()
    h1 = lines[0] if lines else ''
    exp = f'# Chapter {num}:'
    if not h1.startswith(exp):
        bad.append(f'{f}: H1={h1!r}')
    title = h1.split(':', 1)[1].strip() if h1.startswith('# Chapter') else ''
    # special chars check
    for ch in ['#', '—', '–', '&', ':', '(', ')']:
        if ch in title:
            bad.append(f'{f}: special char {ch!r} in title {title!r}')
    if title.startswith('The '):
        the_count += 1
    # hash-leading body lines
    for i, ln in enumerate(lines[1:], start=2):
        if ln.startswith('#'):
            bad.append(f'{f}: hash-leading line {i}: {ln[:60]!r}')
print(f'files: {len(files)}')
print(f'The-starting titles: {the_count} / {len(files)} = {the_count/len(files)*100:.0f}%')
if bad:
    print('ISSUES:')
    for b in bad:
        print(' ', b)
else:
    print('FORMAT AUDIT: all clean')
