#!/usr/bin/env python3
"""Pick candidate classic pairs seeded by current timestamp (cron factory)."""
import random, re, sys

SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 1789362022
rng = random.Random(SEED)

titles = []
with open('/root/世界名著大全.md', encoding='utf-8') as f:
    for line in f:
        for m in re.finditer(r'《([^》]+)》', line):
            titles.append(m.group(1).strip())

titles = list(dict.fromkeys(titles))
print(f"parsed {len(titles)} classics")

# sample 4 candidate pairs
pairs = []
pool = titles[:]
for i in range(4):
    if len(pool) < 2:
        break
    a = rng.choice(pool)
    pool.remove(a)
    b = rng.choice(pool)
    pool.remove(b)
    pairs.append((a, b))

for i, (a, b) in enumerate(pairs):
    print(f"PAIR{i+1}: {a} × {b}")
