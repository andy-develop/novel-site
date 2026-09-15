#!/usr/bin/env python3
"""Cron factory: sample candidate classic pairs with a given seed."""
import random, re, sys

SRC = "/root/世界名著大全.md"
seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1788775276
random.seed(seed)

text = open(SRC, encoding="utf-8").read()
titles = re.findall(r"《([^》]+)》", text)
titles = [t.strip() for t in titles if t.strip()]
print(f"parsed {len(titles)} classics")

pairs = []
seen = set()
while len(pairs) < 6:
    a, b = random.sample(titles, 2)
    key = tuple(sorted((a, b)))
    if key in seen:
        continue
    seen.add(key)
    pairs.append((a, b))

for i, (a, b) in enumerate(pairs, 1):
    print(f"PAIR{i}: {a} || {b}")
