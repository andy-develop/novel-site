#!/usr/bin/env python3
"""Phase 1: sample classic pairs with timestamp seed."""
import re, random, sys, json

with open('/root/世界名著大全.md', encoding='utf-8') as f:
    text = f.read()
titles = re.findall(r'《([^》]+)》\s*\|', text)
authors = re.findall(r'《[^》]+》\s*\|\s*([^\n|]+)', text)
books = list(zip(titles, authors))
print(f"total classics: {len(books)}")

seed = int(sys.argv[1]) if len(sys.argv) > 1 else int(__import__('time').time())
random.seed(seed)
print(f"seed: {seed}")

# sample 8 distinct books, form 4 pairs
idx = random.sample(range(len(books)), 8)
pairs = []
for i in range(0, 8, 2):
    a, b = books[idx[i]], books[idx[i+1]]
    pairs.append((a, b))
    print(f"PAIR {i//2+1}: 《{a[0]}》 | {a[1]}  x  《{b[0]}》 | {b[1]}")
