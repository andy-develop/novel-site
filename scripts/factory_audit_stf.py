#!/usr/bin/env python3
"""Read-only format audit: H1 contract, forbidden chars, body markdown, paragraph length, word counts."""
import re, glob, sys

files = sorted(glob.glob('/root/novels/stain-the-fan/chapters/ch*.md'))
problems = []
total = 0
for f in files:
    n = int(re.search(r'ch(\d+)\.md', f).group(1))
    lines = open(f, encoding='utf-8').read().splitlines()
    h1 = lines[0] if lines else ''
    words = len(' '.join(lines).split())
    total += words
    if not re.fullmatch(r'# Chapter \d+: .+', h1):
        problems.append(f'{f}: BAD H1: {h1!r}')
    m = re.search(r'# Chapter (\d+): (.*)', h1)
    if m:
        t = m.group(2)
        if re.search(r'[#—–&:()]', t):
            problems.append(f'{f}: FORBIDDEN CHAR in title: {t!r}')
        if int(m.group(1)) != n:
            problems.append(f'{f}: H1 number {m.group(1)} != filename {n}')
    body = lines[1:]
    for i, ln in enumerate(body, start=2):
        if ln.startswith('#'):
            problems.append(f'{f}:{i}: hash-leading line: {ln[:60]!r}')
        if re.search(r'\*{1,3}', ln):
            problems.append(f'{f}:{i}: asterisk: {ln[:60]!r}')
        if re.fullmatch(r'-{3,}|\*{3,}|_{3,}', ln.strip()):
            problems.append(f'{f}:{i}: scene divider')
    # paragraph length: consecutive non-empty lines
    plen = 0
    for ln in body:
        if ln.strip():
            plen += 1
            if plen > 6:
                problems.append(f'{f}: paragraph >6 lines (around line {body.index(ln)+2})')
                break
        else:
            plen = 0
    if words < 1300:
        problems.append(f'{f}: SHORT {words} words')
    print(f'{f}: {words} words | {h1}')
print(f'TOTAL: {total} words over {len(files)} files')
print(f'PROBLEMS: {len(problems)}')
for p in problems:
    print(' -', p)
