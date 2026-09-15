#!/usr/bin/env python3
"""Pick random classic pairs from 世界名著大全.md with a given seed."""
import re, sys, random

text = open('/root/世界名著大全.md', encoding='utf-8').read()
titles = re.findall(r'《([^》]+)》\s*\|', text)
titles = list(dict.fromkeys(titles))  # dedupe, keep order
print(f"parsed {len(titles)} titles", file=sys.stderr)

seed = int(sys.argv[1]) if len(sys.argv) > 1 else 42
random.seed(seed)

# sample 6 candidate pairs (distinct titles)
pairs = []
used = set()
while len(pairs) < 6:
    a, b = random.sample(titles, 2)
    key = tuple(sorted((a, b)))
    if key in used:
        continue
    used.add(key)
    pairs.append((a, b))

for i, (a, b) in enumerate(pairs, 1):
    print(f"PAIR{i}: {a} × {b}")
