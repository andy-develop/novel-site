#!/usr/bin/env python3
"""Cron batch factory Phase 1: sample classic pairs with timestamp seed (dedupe, 8 pairs)."""
import random, re, sys, datetime

src = open('/root/世界名著大全.md', encoding='utf-8').read()
titles = re.findall(r'《([^》]+)》', src)
titles = list(dict.fromkeys(titles))  # dedupe, keep order
print(f"parsed {len(titles)} unique titles", file=sys.stderr)

seed = int(datetime.datetime.now().timestamp())
rng = random.Random(seed)
print(f"seed={seed}", file=sys.stderr)

pairs = []
seen = set()
while len(pairs) < 8:
    a, b = rng.sample(titles, 2)
    key = tuple(sorted([a, b]))
    if key in seen:
        continue
    seen.add(key)
    pairs.append((a, b))

for i, (a, b) in enumerate(pairs, 1):
    print(f"PAIR{i}: {a} x {b}")
