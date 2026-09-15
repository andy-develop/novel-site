#!/usr/bin/env python3
"""Re-copy two patched expansion files into chapters/, fixing H1 numbers."""
import os, re

BASE = '/root/novels/no-one-is-coming/chapters'
EXP = '/root/novels/no-one-is-coming/outlines/expansion'

fixes = {
    'tobi-version.md': 27,
    'yara-version.md': 29,
}
for src, fin in fixes.items():
    text = open(os.path.join(EXP, src), encoding='utf-8').read()
    lines = text.split('\n')
    if lines[0].startswith('# Chapter'):
        lines[0] = re.sub(r'^# Chapter \d+:', f'# Chapter {fin}:', lines[0])
    out = '\n'.join(lines)
    open(os.path.join(BASE, f'ch{fin:03d}.md'), 'w', encoding='utf-8').write(out)
    print(f"wrote ch{fin:03d}.md H1: {lines[0]}")

# verify
for fin in (27, 29):
    first = open(os.path.join(BASE, f'ch{fin:03d}.md'), encoding='utf-8').readline().strip()
    print(f"ch{fin:03d} H1: {first}")
