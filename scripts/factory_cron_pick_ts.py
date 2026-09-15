#!/usr/bin/env python3
"""Phase 1: pick classic pairs with a time-based seed, score them via rubric."""
import re, random, sys, time

text = open('/root/世界名著大全.md').read()
titles = re.findall(r'《([^》]+)》', text)
titles = list(dict.fromkeys(titles))
print("parsed titles:", len(titles))

seed = int(time.time())
print("seed:", seed, "time:", time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(seed)))
random.seed(seed)

# sample 4 pairs
pairs = []
picked = set()
while len(pairs) < 4:
    a, b = random.sample(titles, 2)
    key = tuple(sorted([a, b]))
    if key in picked:
        continue
    picked.add(key)
    pairs.append((a, b))

for i, (a, b) in enumerate(pairs, 1):
    print(f"PAIR{i}: 《{a}》 × 《{b}》")
