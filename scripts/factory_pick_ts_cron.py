#!/usr/bin/env python3
"""Factory pick: sample 5 candidate pairs with timestamp seed (cron run)."""
import re, random, time

src = open('/root/世界名著大全.md', encoding='utf-8').read()
titles = re.findall(r'《([^》]+)》', src)
titles = list(dict.fromkeys(titles))
print(f"parsed {len(titles)} titles")

seed = int(time.time())
random.seed(seed)
print(f"seed: {seed}")

seen = set()
pairs = []
while len(pairs) < 5 and len(seen) < 400:
    a, b = random.sample(titles, 2)
    key = tuple(sorted([a, b]))
    if key in seen:
        continue
    seen.add(key)
    pairs.append((a, b))

for i, (a, b) in enumerate(pairs, 1):
    print(f"PAIR {i}: 《{a}》 + 《{b}》")
