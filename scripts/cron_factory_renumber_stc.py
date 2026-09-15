#!/usr/bin/env python3
"""Renumber chapters after inserting a new ch19: shift old 20..28 -> 21..29, fix H1s."""
import os, re

d = '/root/novels/strip-the-coat/chapters'
# reverse order so no target filename is occupied
for old in range(28, 19, -1):
    src = os.path.join(d, f'ch{old:03d}.md')
    dst = os.path.join(d, f'ch{old+1:03d}.md')
    if not os.path.exists(src):
        print('MISSING', src)
        continue
    txt = open(src, encoding='utf-8').read()
    lines = txt.split('\n')
    m = re.match(r'^# Chapter \d+:', lines[0])
    if m:
        rest = lines[0][m.end():]
        lines[0] = f'# Chapter {old+1}:{rest}'
    else:
        print('NO H1', src, lines[0][:50])
    open(dst, 'w', encoding='utf-8').write('\n'.join(lines))
    os.remove(src)
    print(f'ch{old:03d} -> ch{old+1:03d}: {lines[0]}')
print('DONE')
