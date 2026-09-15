#!/usr/bin/env python3
"""Phase 1: parse 世界名著大全.md, sample 4 candidate pairs with timestamp seed."""
import re, random, time, sys

text = open('/root/世界名著大全.md', encoding='utf-8').read()
titles = []
for line in text.splitlines():
    for m in re.finditer(r'《([^》]+)》', line):
        t = m.group(1).strip()
        if t and t not in titles:
            titles.append(t)
print(f"parsed {len(titles)} titles")

seed = int(time.time())
print("seed:", seed)
random.seed(seed)
pairs = []
seen = set()
while len(pairs) < 4:
    a, b = random.sample(titles, 2)
    key = tuple(sorted((a, b)))
    if key in seen:
        continue
    seen.add(key)
    pairs.append((a, b))

for i, (a, b) in enumerate(pairs, 1):
    print(f"PAIR {i}: 《{a}》 × 《{b}》")
