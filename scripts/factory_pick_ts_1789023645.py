#!/usr/bin/env python3
"""Cron factory Phase 1: sample classic pairs with timestamp seed."""
import random, re, sys

seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1789023645
src = open('/root/世界名著大全.md', encoding='utf-8').read()
titles = re.findall(r'《([^》]+)》\s*\|\s*([^\n|]+)', src)
uniq = {}
for t, a in titles:
    uniq.setdefault(t.strip(), a.strip())
items = list(uniq.items())
print(f"seed={seed} unique_titles={len(items)}")

rng = random.Random(seed)
pairs = []
seen = set()
for _ in range(6):
    a, b = rng.sample(items, 2)
    key = tuple(sorted([a[0], b[0]]))
    if key in seen:
        continue
    seen.add(key)
    pairs.append((a, b))

for i, (a, b) in enumerate(pairs, 1):
    print(f"PAIR{i}: 《{a[0]}》|{a[1]}  ×  《{b[0]}》|{b[1]}")
