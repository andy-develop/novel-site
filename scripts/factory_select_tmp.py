#!/usr/bin/env python3
"""Phase 1: sample 4 random classic pairs, seeded by current timestamp."""
import re, random, sys

text = open('/root/世界名著大全.md', encoding='utf-8').read()
entries = []
seen = set()
for line in text.splitlines():
    m = re.search(r'《([^》]+)》\s*\|\s*([^|]+?)\s*\|?$', line.strip())
    if m:
        t = m.group(1).strip()
        a = m.group(2).strip()
        if t not in seen:
            seen.add(t)
            entries.append((t, a))

print("total entries:", len(entries))
seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1788573642
random.seed(seed)

titles = [e[0] for e in entries]
sample = random.sample(titles, 8)
amap = dict(entries)
pairs = [(sample[i], sample[i+1]) for i in range(0, 8, 2)]
print(f"seed={seed}")
for i, (a, b) in enumerate(pairs, 1):
    print(f"PAIR{i}: 《{a}》({amap[a]}) x 《{b}》({amap[b]})")
