#!/usr/bin/env python3
"""Sample candidate classic pairs using timestamp seed."""
import random, re, sys

text = open('/root/世界名著大全.md', encoding='utf-8').read()
titles = re.findall(r'《([^》]+)》\s*\|\s*([^|\n]+)', text)
print("parsed:", len(titles))

seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1789131652
random.seed(seed)

# exclude pairs already used in past novels (rough list of over-used classics)
used = set()
for i in range(5):
    pairs = []
    idx = list(range(len(titles)))
    random.shuffle(idx)
    for j in range(4):
        a = idx[2*j]; b = idx[2*j+1]
        pairs.append((titles[a], titles[b]))
    print(f"--- roll {i+1} (seed {seed+i}) ---")
    for p in pairs:
        print(f"  {p[0][0]} | {p[0][1]}  X  {p[1][0]} | {p[1][1]}")
    random.seed(seed + i + 1)
