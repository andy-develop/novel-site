#!/usr/bin/env python3
"""Renumber ch019-024 -> ch021-026 (reverse order) and rewrite H1 prefixes."""
import os, re

d = '/root/novels/the-white-echo/chapters'
# reverse order to avoid collisions
for old_n in range(24, 18, -1):
    new_n = old_n + 2
    old = os.path.join(d, f'ch{old_n:03d}.md')
    new = os.path.join(d, f'ch{new_n:03d}.md')
    assert os.path.exists(old), old
    assert not os.path.exists(new), f'target exists {new}'
    lines = open(old, encoding='utf-8').read().split('\n')
    # rewrite H1 prefix Chapter N: -> Chapter N+2:
    m = re.match(r'^# Chapter (\d+): (.*)$', lines[0])
    assert m and int(m.group(1)) == old_n, f'bad H1 {lines[0]}'
    lines[0] = f'# Chapter {new_n}: {m.group(2)}'
    open(new, 'w', encoding='utf-8').write('\n'.join(lines))
    os.remove(old)
    print(f'ch{old_n:03d} -> ch{new_n:03d}  {lines[0]}')
print('done')
