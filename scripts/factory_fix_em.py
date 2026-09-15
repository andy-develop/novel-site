#!/usr/bin/env python3
"""Replace em dashes with commas in the 3 orchestrator-written chapters."""
import re

for f in ['ch025.md', 'ch026.md', 'ch027.md']:
    p = f'/root/novels/everyone-lied-about-june/chapters/{f}'
    with open(p, encoding='utf-8') as fh:
        t = fh.read()
    before = t.count('\u2014')
    # em dash surrounded by spaces -> comma; other em dashes -> comma too
    t2 = t.replace('\u2014', ',')
    with open(p, 'w', encoding='utf-8') as fh:
        fh.write(t2)
    print(f'{f}: replaced {before} em dashes')
