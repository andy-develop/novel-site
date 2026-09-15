#!/usr/bin/env python3
"""Audit chapter files: H1 first line, filename match, body markdown, word counts."""
import os, re, sys

d = sys.argv[1] if len(sys.argv) > 1 else "/root/novels/midnight-upload/chapters"
files = sorted(f for f in os.listdir(d) if re.fullmatch(r'ch\d{3}\.md', f))
print(f"{len(files)} chapter files")
bad_h1, bad_md, thin, total = [], [], [], 0
for f in files:
    n = int(re.search(r'ch(\d{3})', f).group(1))
    lines = open(os.path.join(d, f), encoding='utf-8').read().split('\n')
    words = len(lines and ' '.join(l for l in lines if l.strip()).split())
    total += words
    if not lines or not lines[0].startswith(f'# Chapter {n}:'):
        bad_h1.append((f, lines[0][:60] if lines else 'EMPTY'))
    # body lines starting with # (other than first line)
    body = lines[1:]
    md = [l for l in body if l.strip().startswith('#')]
    if md:
        bad_md.append((f, md[:3]))
    if words < 1300:
        thin.append((f, words))
    # special chars in title
    t = lines[0][len(f'# Chapter {n}:'):].strip() if lines else ''
    for ch in '#-–&:()':
        if ch in t:
            print(f"  TITLE-CHAR {f}: {t!r} contains {ch!r}")
print(f"TOTAL WORDS: {total}")
print("BAD H1:", bad_h1 if bad_h1 else "none")
print("BODY # LINES:", bad_md if bad_md else "none")
print("THIN (<1300):", thin if thin else "none")
# title pattern check: count titles starting with 'The'
thes = []
for f in files:
    lines = open(os.path.join(d, f), encoding='utf-8').read().split('\n')
    if lines and lines[0].startswith('# Chapter'):
        t = lines[0].split(':', 1)[1].strip()
        if t.startswith('The '):
            thes.append((f, t))
print(f"'The'-openers: {len(thes)}/{len(files)} = {100*len(thes)//len(files)}%", thes)
