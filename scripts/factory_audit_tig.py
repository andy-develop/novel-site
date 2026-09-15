#!/usr/bin/env python3
"""Audit chapter format: H1 titles, special chars, The-count, patterns, bad body lines."""
import re, os, glob

D = '/root/novels/the-improbability-garden/chapters'
files = sorted(glob.glob(os.path.join(D, 'ch[0-9][0-9][0-9].md')))
print(f"files: {len(files)}")
titles = []
problems = []
for f in files:
    n = int(re.search(r'ch(\d{3})', f).group(1))
    lines = open(f, encoding='utf-8').read().split('\n')
    h1 = lines[0]
    m = re.match(r'^# Chapter (\d+): (.+)$', h1)
    if not m:
        problems.append(f"BAD H1 {f}: {h1[:80]!r}")
        continue
    num, title = int(m.group(1)), m.group(2)
    if num != n:
        problems.append(f"H1 NUM MISMATCH {f}: H1 says {num}")
    titles.append((n, title))
    # special chars in title part
    if re.search(r'[#—–&:()]', title):
        problems.append(f"SPECIAL CHARS {f}: {title!r}")
    if title.endswith('.'):
        problems.append(f"TRAILING PERIOD {f}: {title!r}")
    # body checks
    body = lines[1:]
    for i, ln in enumerate(body, 2):
        s = ln.strip()
        if not s:
            continue
        if s.startswith('#'):
            problems.append(f"HASH BODY LINE {f}:{i}: {s[:60]!r}")
        if re.search(r'\*\*|^\s*\*|^\s*---|^\s*$', ln) and ('**' in ln or ln.strip().startswith('*')):
            problems.append(f"ASTERISK {f}:{i}: {ln.strip()[:60]!r}")
        if re.search(r'^---+$', s):
            problems.append(f"SCENE DIVIDER {f}:{i}")

print("--- titles ---")
for n, t in titles:
    print(f"ch{n:03d}: {t}")
the_count = sum(1 for _, t in titles if t.startswith('The '))
print(f"\nThe-openers: {the_count}/{len(titles)} = {the_count/len(titles)*100:.1f}%")
if problems:
    print("--- PROBLEMS ---")
    for p in problems:
        print(p)
else:
    print("no problems")
