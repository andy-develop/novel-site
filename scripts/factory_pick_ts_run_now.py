#!/usr/bin/env python3
"""Pick 2 random classics from the master list, seeded by a timestamp arg."""
import random
import re
import sys

LIST = "/root/世界名著大全.md"
seed = int(sys.argv[1]) if len(sys.argv) > 1 else 42
text = open(LIST, encoding="utf-8").read()
titles = re.findall(r"《([^》]+)》", text)
titles = [t.strip() for t in titles if t.strip()]
print(f"total classics parsed: {len(titles)}")

random.seed(seed)
seen = set()
pairs = []
while len(pairs) < 6:
    a, b = random.sample(titles, 2)
    key = tuple(sorted([a, b]))
    if key in seen:
        continue
    seen.add(key)
    pairs.append((a, b))

for i, (a, b) in enumerate(pairs, 1):
    print(f"PAIR {i}: 《{a}》 x 《{b}》")
