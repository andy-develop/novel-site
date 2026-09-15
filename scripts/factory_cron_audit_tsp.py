#!/usr/bin/env python3
"""Audit chapters: word counts, H1 format, special chars, markdown violations."""
import glob, re, os

files = sorted(glob.glob('/root/novels/the-shining-prince/chapters/ch*.md'))
total = 0
problems = []
titles = []
for f in files:
    n = int(re.search(r'ch(\d+)\.md', f).group(1))
    lines = open(f, encoding='utf-8').read().split('\n')
    words = len(open(f, encoding='utf-8').read().split())
    total += words
    h1 = lines[0].strip()
    expected = f'# Chapter {n}:'
    if not h1.startswith(expected):
        problems.append(f'{os.path.basename(f)}: BAD H1: {h1!r}')
    title = h1[len(expected):].strip()
    titles.append(title)
    if words < 1300:
        problems.append(f'{os.path.basename(f)}: TOO SHORT {words}w')
    # body check: lines starting with # (other than first), asterisks
    for i, ln in enumerate(lines[1:], 2):
        if ln.startswith('#'):
            problems.append(f'{os.path.basename(f)}: hash-leading line {i}: {ln[:60]!r}')
        if '*' in ln:
            problems.append(f'{os.path.basename(f)}: asterisk line {i}')
    # title special chars
    if re.search(r'[#—–&:()]', title):
        problems.append(f'{os.path.basename(f)}: TITLE SPECIAL CHARS: {title!r}')

print(f'files={len(files)} total_words={total}')
the_count = sum(1 for t in titles if t.startswith('The '))
print(f'titles starting with "The": {the_count}/{len(titles)} = {the_count/len(titles)*100:.0f}%')
print('TITLES:', ' | '.join(titles))
if problems:
    print('PROBLEMS:')
    for p in problems:
        print(' -', p)
else:
    print('NO PROBLEMS')
