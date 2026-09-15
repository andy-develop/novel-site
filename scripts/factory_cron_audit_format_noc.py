#!/usr/bin/env python3
"""Audit chapter files: hash-leading body lines, asterisks, weird chars in body."""
import os, re

BASE = '/root/novels/no-one-is-coming/chapters'
issues = 0
for f in sorted(os.listdir(BASE)):
    if not re.fullmatch(r'ch\d{3}\.md', f):
        continue
    lines = open(os.path.join(BASE, f), encoding='utf-8').read().split('\n')
    for i, ln in enumerate(lines):
        if i == 0:
            continue  # H1
        s = ln.strip()
        if s.startswith('#'):
            print(f"{f}:{i+1} hash-leading body line: {s[:60]}")
            issues += 1
        if '*' in s or '**' in s:
            print(f"{f}:{i+1} asterisk: {s[:60]}")
            issues += 1
        if '—' in s or '–' in s:
            # em dashes in body are OK per style, but flag them in case
            pass
print("issues:", issues)
