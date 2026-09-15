#!/usr/bin/env python3
"""Pick candidate classic pairs using timestamp seed."""
import random
import re
import sys

with open("/root/世界名著大全.md", encoding="utf-8") as f:
    text = f.read()

entries = re.findall(r"《([^》]+)》\s*\|\s*([^|\n]+)", text)
seen = set()
books = []
for title, author in entries:
    t = title.strip()
    a = author.strip()
    if t and (t, a) not in seen:
        seen.add((t, a))
        books.append((t, a))

print("TOTAL_BOOKS:", len(books))

seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1788904846
random.seed(seed)

# sample 6 pairs (need 5 rolls max, keep extra buffer)
pairs = []
used = set()
for _ in range(6):
    for _try in range(200):
        a, b = random.sample(books, 2)
        key = tuple(sorted([a[0], b[0]]))
        if key not in used:
            used.add(key)
            pairs.append((a, b))
            break

for i, (a, b) in enumerate(pairs, 1):
    print(f"PAIR{i}: 《{a[0]}》 | {a[1]}  ×  《{b[0]}》 | {b[1]}")
