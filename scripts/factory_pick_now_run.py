#!/usr/bin/env python3
"""Parse 世界名著大全.md, sample 4 candidate pairs with a timestamp seed."""
import re, random, sys, time

text = open("/root/世界名著大全.md", encoding="utf-8").read()
titles = re.findall(r"《([^》]+)》", text)
seen = []
for t in titles:
    if t not in seen:
        seen.append(t)
print("total_unique_titles:", len(seen))

seed = int(time.time())
random.seed(seed)
print("seed:", seed, "|", time.strftime("%Y-%m-%d %H:%M:%S"))

# sample 4 candidate pairs (distinct works)
pairs = []
pool = list(seen)
random.shuffle(pool)
for i in range(4):
    a = pool[i * 2]
    b = pool[i * 2 + 1]
    pairs.append((a, b))
for i, (a, b) in enumerate(pairs, 1):
    print(f"PAIR{i}: 《{a}》 × 《{b}》")
