#!/usr/bin/env python3
"""Strip asterisks from chapter bodies (emphasis artifacts)."""
import re, sys

for f in ['/root/novels/where-the-smoke-went/chapters/ch025.md',
          '/root/novels/where-the-smoke-went/chapters/ch027.md']:
    lines = open(f, encoding='utf-8').read().split('\n')
    out = [re.sub(r'\*+', '', ln) for ln in lines]
    open(f, 'w', encoding='utf-8').write('\n'.join(out))
    print('stripped:', f)
