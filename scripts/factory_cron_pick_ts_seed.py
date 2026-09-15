#!/usr/bin/env python3
"""Pick 5 classic pairs from 世界名著大全.md using seed = current timestamp."""
import re, random, sys, datetime

src = "/root/世界名著大全.md"
text = open(src, encoding="utf-8").read()
titles = re.findall(r"《([^》]+)》", text)
# dedupe keeping order
seen = set()
uniq = []
for t in titles:
    if t not in seen:
        seen.add(t)
        uniq.append(t)
print(f"TOTAL_UNIQUE: {len(uniq)}")

seed = int(datetime.datetime.now().timestamp())
print(f"SEED: {seed}")
rng = random.Random(seed)
# sample 8 titles, form 4 pairs
titles_pool = rng.sample(uniq, 8)
pairs = [(titles_pool[i], titles_pool[i+1]) for i in range(0, 8, 2)]
# also 2 more pairs from a fresh shuffle for variety
extra = rng.sample(uniq, 8)
pairs += [(extra[i], extra[i+1]) for i in range(0, 8, 2)]
for i, (a, b) in enumerate(pairs, 1):
    print(f"PAIR{i}: 《{a}》 × 《{b}》")
