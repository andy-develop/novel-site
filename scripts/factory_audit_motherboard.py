#!/usr/bin/env python3
"""Audit chapters: word count, H1 format, title special chars, body markdown."""
import re, glob, sys

files = sorted(glob.glob('/root/novels/motherboard/chapters/ch*.md'))
total = 0
bad_h1 = []
bad_titles = []
body_hash = []
body_md = []
the_starters = 0
for f in files:
    lines = open(f, encoding='utf-8').read().split('\n')
    total += sum(len(l.split()) for l in lines)
    h1 = lines[0]
    m = re.match(r'^# Chapter (\d+): (.+)$', h1)
    if not m:
        bad_h1.append(f)
        continue
    n = int(m.group(1))
    title = m.group(2)
    if re.search(r'[—–&:()#]', title):
        bad_titles.append((f, title))
    if title.startswith('The '):
        the_starters += 1
    for i, l in enumerate(lines[1:], 2):
        if l.startswith('#'):
            body_hash.append((f, i))
        if re.match(r'^(\*|>|!\[)', l) or re.match(r'^-{3,}$', l):
            body_md.append((f, i))
print(f"FILES: {len(files)}  TOTAL_WORDS: {total}")
print(f"BAD_H1: {bad_h1}")
print(f"BAD_TITLES: {bad_titles}")
print(f"BODY_HASH: {body_hash}")
print(f"BODY_MD: {body_md}")
print(f"THE_STARTERS: {the_starters} / {len(files)}")
for f in files:
    w = sum(len(l.split()) for l in open(f, encoding='utf-8').read().split('\n'))
    if w < 1600:
        print(f"  THIN: {f} = {w}")
print("AUDIT DONE")
