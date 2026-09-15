#!/usr/bin/env python3
"""Sample classic pairs from 世界名著大全 with timestamp seed. Cron-safe."""
import re, random, sys
seed = int(sys.argv[1]) if len(sys.argv) > 1 else int(open('/dev/urandom').read(4).hex(), 16) % 2**32
random.seed(seed)
txt = open('/root/世界名著大全.md').read()
titles = re.findall(r'《([^》]+)》', txt)
# dedupe preserving order
seen = set(); uniq = []
for t in titles:
    if t not in seen:
        seen.add(t); uniq.append(t)
print('SEED', seed, 'UNIQUE_TITLES', len(uniq))
for i in range(6):
    a, b = random.sample(uniq, 2)
    print(f'PAIR{i+1}: {a}  ×  {b}')
