#!/usr/bin/env python3
"""Fix ' ,' / ',,' artifacts from em-dash replacement; report remaining counts."""
import re
for f in ['ch025.md', 'ch026.md', 'ch027.md']:
    p = f'/root/novels/everyone-lied-about-june/chapters/{f}'
    with open(p, encoding='utf-8') as fh:
        t = fh.read()
    t2 = t.replace(' ,', ',').replace(',,', ',')
    # also clean double spaces
    t2 = re.sub(r'  +', ' ', t2)
    if t2 != t:
        with open(p, 'w', encoding='utf-8') as fh:
            fh.write(t2)
        print(f'{f}: cleaned artifacts')
    else:
        print(f'{f}: clean')
