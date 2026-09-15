#!/usr/bin/env python3
"""Audit chapter files: H1 contract, banned chars, hash-lines, dividers, word counts."""
import re, glob, os

d = '/root/novels/counterfeit-hearts/chapters'
files = sorted(glob.glob(os.path.join(d, 'ch*.md')))
print(f"file_count={len(files)}")
assert len(files) == 28, "need 28 chapters"

total = 0
titles = []
problems = []
for f in files:
    n = os.path.basename(f)
    lines = open(f, encoding='utf-8').read().splitlines()
    # H1
    h1 = lines[0] if lines else ''
    m = re.match(r'^# Chapter (\d+): (.+)$', h1)
    if not m:
        problems.append(f"{n}: BAD H1: {h1!r}")
        titles.append('')
        continue
    num, title = int(m.group(1)), m.group(2)
    titles.append(title)
    # filename number must match H1 number
    fnum = int(re.search(r'ch(\d+)', n).group(1))
    if fnum != num:
        problems.append(f"{n}: H1 says Chapter {num}")
    # banned chars in title
    if re.search(r'[#—–&:()]', title):
        problems.append(f"{n}: BANNED CHAR in title: {title!r}")
    if '  ' in title:
        problems.append(f"{n}: double space in title: {title!r}")
    # body checks
    body = lines[1:]
    for i, ln in enumerate(body, start=2):
        if ln.startswith('#'):
            problems.append(f"{n}:{i}: hash-leading body line: {ln[:60]!r}")
        if re.search(r'\*|_', ln):
            problems.append(f"{n}:{i}: markdown char in body: {ln[:60]!r}")
        if re.match(r'^(\*\*\*|---|\*\*\*+)\s*$', ln):
            problems.append(f"{n}:{i}: scene divider")
    # word count
    wc = len(re.findall(r'\S+', ' '.join(body)))
    total += wc
    if wc < 1300:
        problems.append(f"{n}: THIN {wc} words")

print(f"total_words={total}")
print(f"avg={total//len(files)}")
# title pattern audit
the_count = sum(1 for t in titles if t.startswith('The '))
print(f"the_starters={the_count}/{len(titles)} = {the_count/len(titles)*100:.0f}%")
for i, t in enumerate(titles, 1):
    print(f"ch{i:03d}: {t}")
if problems:
    print("--- PROBLEMS ---")
    for p in problems:
        print(p)
else:
    print("NO PROBLEMS")
