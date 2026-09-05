#!/usr/bin/env python3
"""Sample classic pairs with timestamp seed for batch novel factory Phase 1."""
import random, re, sys

seed = int(sys.argv[1]) if len(sys.argv) > 1 else int(__import__('time').time())
titles = []
for line in open('/root/世界名著大全.md', encoding='utf-8'):
    for m in re.finditer(r'《([^》]+)》', line):
        titles.append(m.group(1))

# dedupe keeping order
seen = set()
uniq = []
for t in titles:
    if t not in seen:
        seen.add(t)
        uniq.append(t)

print(f"total unique classics: {len(uniq)}")
rng = random.Random(seed)
# shuffle the whole list once (timestamp seed), then draw 4 pairs of 2
pool = uniq[:]
rng.shuffle(pool)
pairs = []
for i in range(4):
    pairs.append((pool[2*i], pool[2*i+1]))
for idx, (a, b) in enumerate(pairs, 1):
    print(f"PAIR {idx}: {a} × {b}")
