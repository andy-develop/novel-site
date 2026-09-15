#!/usr/bin/env python3
"""Phase 1: sample classic pairs from 世界名著大全 with seed=current timestamp."""
import re, random, sys

seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1788973225
random.seed(seed)

books = []
with open("/root/世界名著大全.md") as f:
    for line in f:
        m = re.search(r"《([^》]+)》\s*\|\s*([^|]+)", line)
        if m:
            books.append((m.group(1).strip(), m.group(2).strip()))

print(f"parsed {len(books)} books")
# sample 8 unique titles, form 4 pairs
titles = random.sample(books, 8)
for i in range(0, 8, 2):
    a, b = titles[i], titles[i+1]
    print(f"PAIR{i//2+1}: 《{a[0]}》 | {a[1]}  X  《{b[0]}》 | {b[1]}")
