#!/usr/bin/env python3
"""Phase 1 (unique run): parse classics list, sample 4 candidate pairs with timestamp seed."""
import re, random, time

src = open('/root/世界名著大全.md', encoding='utf-8').read()
titles = re.findall(r'《([^》]+)》\s*\|([^|]+)', src)
items = [(t.strip(), a.strip()) for t, a in titles]
print(f'parsed {len(items)} classics')

seed = int(time.time())
print(f'seed={seed}')
random.seed(seed)

pairs = []
while len(pairs) < 4:
    a, b = random.sample(items, 2)
    pair = (a, b)
    if pair not in pairs and (b, a) not in pairs:
        pairs.append(pair)

for i, (a, b) in enumerate(pairs, 1):
    print(f'--- pair {i} ---')
    print(f'  A: {a[0]} | {a[1]}')
    print(f'  B: {b[0]} | {b[1]}')
