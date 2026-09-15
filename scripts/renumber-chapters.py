#!/usr/bin/env python3
"""Renumber chapters (reverse order to avoid clobber), rewrite H1 prefixes."""
import re, os, sys, glob

d = sys.argv[1] if len(sys.argv) > 1 else '/root/novels/unreadable/chapters'
mapping = {}  # old -> new
for arg in sys.argv[2:]:
    old, new = arg.split('=')
    mapping[old.strip()] = new.strip()

for old, new in sorted(mapping.items(), key=lambda kv: kv[0], reverse=True):
    oldp = os.path.join(d, old)
    newp = os.path.join(d, new)
    if not os.path.exists(oldp):
        print(f'MISSING {oldp}')
        continue
    txt = open(oldp, encoding='utf-8').read()
    # rewrite H1 "# Chapter N:" prefix -> new number
    m = re.match(r'^# Chapter (\d+):([^\n]*)$', txt, re.MULTILINE)
    if m:
        num = new.replace('ch', '').replace('.md', '').lstrip('0')
        txt = f'# Chapter {num}:{m.group(2)}' + txt[m.end():]
    with open(newp, 'w', encoding='utf-8') as f:
        f.write(txt)
    os.remove(oldp)
    print(f'{old} -> {new} (H1: # Chapter {num}:{m.group(2)[:40]})')
