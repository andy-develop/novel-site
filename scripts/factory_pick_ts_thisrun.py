#!/usr/bin/env python3
"""Pick 4 random classic pairs from 世界名著大全.md, seeded by timestamp."""
import random, re, sys, time

seed = int(time.time())
titles = []
for line in open('/root/世界名著大全.md', encoding='utf-8'):
    m = re.search(r'《([^》]+)》\s*\|\s*([^|]+?)\s*\|?\s*$', line.strip())
    if m:
        titles.append((m.group(1).strip(), m.group(2).strip()))

titles = list(dict.fromkeys(titles))
print(f"TOTAL_TITLES={len(titles)} SEED={seed}")

random.seed(seed)
sample = random.sample(titles, 8)
# build 4 pairs from the 8 sampled titles (shuffle, chunk)
random.shuffle(sample)
pairs = [(sample[i], sample[i+1]) for i in range(0, 8, 2)]
for idx, (a, b) in enumerate(pairs, 1):
    print(f"PAIR{idx}: 《{a[0]}》{a[1]}  x  《{b[0]}》{b[1]}")
