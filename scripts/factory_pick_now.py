#!/usr/bin/env python3
"""Pick random classic pairs with timestamp seed. Usage: python3 pick_now.py [n_pairs] [seed]"""
import re, sys, random, time

txt = open('/root/世界名著大全.md', encoding='utf-8').read()
titles = re.findall(r'《([^》]+)》', txt)
# dedupe preserving order
seen = set()
uniq = []
for t in titles:
    if t not in seen:
        seen.add(t)
        uniq.append(t)
print(f"total unique titles: {len(uniq)}")

seed = int(time.time()) if len(sys.argv) < 3 else int(sys.argv[2])
rng = random.Random(seed)
n = int(sys.argv[1]) if len(sys.argv) >= 2 else 4
print(f"seed={seed}")
for i in range(n):
    a, b = rng.sample(uniq, 2)
    print(f"PAIR{i}: 《{a}》 x 《{b}》")
