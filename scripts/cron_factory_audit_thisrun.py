#!/usr/bin/env python3
"""Audit chapter files: H1 format, banned chars, markdown pollution, body # lines."""
import re, glob, os

files = sorted(glob.glob('/root/novels/half-saint-half-fool/chapters/ch*.md'))
print('FILES', len(files))
bad_h1 = []
bad_chars = []
body_hash = []
asterisk = []
for f in files:
    n = os.path.basename(f)
    with open(f, encoding='utf-8') as fh:
        lines = fh.read().split('\n')
    h1 = lines[0].strip() if lines else ''
    if not re.match(r'^# Chapter \d+: .+', h1):
        bad_h1.append((n, h1[:80]))
    if re.search(r'[—–&:()#]', h1):
        bad_chars.append((n, h1[:80]))
    for i, line in enumerate(lines[1:], 2):
        s = line.strip()
        if s.startswith('#'):
            body_hash.append((n, i, s[:60]))
        if '*' in s or '_' in s.replace('_', '', 0) and re.search(r'\*|__|\*\*', s):
            asterisk.append((n, i, s[:60]))
print('BAD_H1', bad_h1 if bad_h1 else 'none')
print('BAD_CHARS_IN_H1', bad_chars if bad_chars else 'none')
print('BODY_HASH_LINES', len(body_hash), body_hash[:5] if body_hash else '')
print('ASTERISK_LINES', len(asterisk), asterisk[:5] if asterisk else '')
