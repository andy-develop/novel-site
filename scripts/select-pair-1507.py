#!/usr/bin/env python3
"""Phase 1 selection: parse classics list, time-seeded random pairs."""
import random, re, time, sys

titles = []
for line in open('/root/世界名著大全.md', encoding='utf-8'):
    for m in re.finditer(r'《([^》]+)》', line):
        titles.append(m.group(1))
titles = sorted(set(titles))
print(f"total distinct titles: {len(titles)}")

seed = int(time.time())
random.seed(seed)
print(f"seed: {seed}")

books = random.sample(titles, 12)
random.shuffle(books)
pairs = [(books[i], books[i+1]) for i in range(0, 12, 2)]
for i, (a, b) in enumerate(pairs):
    print(f"PAIR{i+1}: 《{a}》 × 《{b}》")
