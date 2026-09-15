#!/usr/bin/env python3
"""Audit chapters: H1 format, banned chars, body format, word counts."""
import re, glob, os

d = '/root/novels/truth-score/chapters/'
files = sorted(glob.glob(d + 'ch*.md'))
print("file_count:", len(files))

banned = re.compile(r'[#—–&:()]')
total = 0
problems = []
for f in files:
    name = os.path.basename(f)
    if not re.fullmatch(r'ch\d{3}\.md', name):
        problems.append(f"{name}: BAD FILENAME")
        continue
    with open(f, encoding='utf-8') as fh:
        lines = fh.read().split('\n')
    h1 = lines[0] if lines else ''
    if not re.match(r'^# Chapter \d+: ', h1):
        problems.append(f"{name}: BAD H1: {h1[:50]!r}")
    if '—' in h1 or '–' in h1:
        problems.append(f"{name}: EM DASH IN H1")
    title = h1.replace('# Chapter ', '').split(': ', 1)[-1] if ': ' in h1 else h1
    if banned.search(title):
        problems.append(f"{name}: BANNED CHAR IN TITLE: {title!r}")
    if title.startswith('The '):
        pass  # counted separately
    # body checks
    body = '\n'.join(lines[1:])
    if re.search(r'\*\*|^\s*\*|^\s*#|^-{3,}|^\s*[-*]\s', body, re.M):
        problems.append(f"{name}: MARKDOWN IN BODY")
    words = len(body.split())
    total += words
    if words < 1300:
        problems.append(f"{name}: THIN {words}")

print("total_words:", total)
the_count = 0
titles = []
for f in files:
    with open(f, encoding='utf-8') as fh:
        h1 = fh.readline().strip()
    t = h1.split(': ', 1)[-1] if ': ' in h1 else h1
    titles.append((os.path.basename(f), t))
    if t.startswith('The '):
        the_count += 1
print("The-titles:", the_count, f"({the_count/len(files)*100:.0f}%)")
print("TITLES:")
for n, t in titles:
    print(f"  {n}: {t}")
if problems:
    print("PROBLEMS:")
    for p in problems:
        print(" ", p)
else:
    print("NO PROBLEMS")
