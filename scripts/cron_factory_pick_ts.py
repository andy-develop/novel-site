#!/usr/bin/env python3
"""Phase 1: sample classic pairs from 世界名著大全 with a given seed."""
import random, re, sys

seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1789365630
random.seed(seed)

titles = []
with open('/root/世界名著大全.md', encoding='utf-8') as f:
    for line in f:
        m = re.search(r'《([^》]+)》\s*\|\s*(.+)', line.strip())
        if m:
            titles.append((m.group(1).strip(), m.group(2).strip()))

print(f"parsed {len(titles)} titles")

# avoid pairs already used: read selected_pairs.txt if exists
used = set()
try:
    with open('/root/novel-site/scripts/selected_pairs.txt', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if '×' in line or 'x' in line:
                for sep in [' × ', ' x ', '×', 'x']:
                    if sep in line:
                        a, b = line.split(sep, 1)
                        used.add((a.strip(), b.strip()))
                        break
except FileNotFoundError:
    pass

print(f"used pairs: {len(used)}")

picked = []
for _ in range(20):
    a, b = random.sample(titles, 2)
    key = (a[0], b[0])
    if key in used or (key[1], key[0]) in used:
        continue
    picked.append((a, b))
    if len(picked) >= 8:
        break

for i, (a, b) in enumerate(picked):
    print(f"CAND{i}: 《{a[0]}》 | {a[1]}  ×  《{b[0]}》 | {b[1]}")
