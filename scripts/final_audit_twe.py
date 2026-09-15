#!/usr/bin/env python3
"""Final pre-upload audit: H1s sequential 1-28, no special chars, no body '#', no asterisks."""
import os, re

d = '/root/novels/the-white-echo/chapters'
files = sorted(os.listdir(d))
print('files:', len(files))
problems = []
for i, f in enumerate(files, 1):
    if f != f'ch{i:03d}.md':
        problems.append(f'filename mismatch: {f} vs ch{i:03d}.md')
    lines = open(os.path.join(d, f), encoding='utf-8').read().split('\n')
    m = re.match(r'^# Chapter (\d+): (.+)$', lines[0])
    if not m:
        problems.append(f'{f}: bad H1: {lines[0]!r}')
    else:
        n, title = int(m.group(1)), m.group(2)
        if n != i:
            problems.append(f'{f}: H1 number {n} != {i}')
        if re.search(r'[#—–&:()]', title):
            problems.append(f'{f}: special char in title: {title!r}')
        if title.endswith(('.', ' ')):
            problems.append(f'{f}: title trailing punctuation: {title!r}')
    for j, line in enumerate(lines[1:], 2):
        if line.startswith('#'):
            problems.append(f'{f}: body hash line {j}: {line[:40]!r}')
        if '*' in line:
            problems.append(f'{f}: asterisk at line {j}')
print('problems:', len(problems))
for p in problems[:20]:
    print(' -', p)
words = sum(len(open(os.path.join(d, f), encoding='utf-8').read().split()) for f in files)
print('total words:', words)
