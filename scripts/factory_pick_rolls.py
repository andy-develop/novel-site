#!/usr/bin/env python3
"""Sample multiple seeds for classic pairs (re-rolls)."""
import re, random, sys

text = open('/root/世界名著大全.md', encoding='utf-8').read()
titles = re.findall(r'《([^》]+)》\s*\|', text)
titles = list(dict.fromkeys(titles))

base = int(sys.argv[1]) if len(sys.argv) > 1 else 1788739275
for roll in range(5):
    random.seed(base + roll * 7919)
    pairs = []
    used = set()
    while len(pairs) < 6:
        a, b = random.sample(titles, 2)
        key = tuple(sorted((a, b)))
        if key in used:
            continue
        used.add(key)
        pairs.append((a, b))
    print(f"=== ROLL {roll+1} (seed {base + roll*7919}) ===")
    for i, (a, b) in enumerate(pairs, 1):
        print(f"  {a} × {b}")
