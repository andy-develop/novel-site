#!/usr/bin/env python3
"""Cron helper: parse classics list, sample 5 candidate pairs with timestamp seed."""
import random, re, sys, datetime

seed = int(datetime.datetime.now().timestamp())
random.seed(seed)

text = open('/root/世界名著大全.md', encoding='utf-8').read()
pairs = re.findall(r'《([^》]+)》\s*\|\s*([^\n|]+)', text)
# dedupe by title
seen = {}
for t, a in pairs:
    seen.setdefault(t.strip(), a.strip())
books = [(t, a) for t, a in seen.items()]
print('PARSED', len(books), 'seed', seed, flush=True)

candidates = []
used = set()
for i in range(5):
    for _ in range(200):
        a, b = random.sample(books, 2)
        key = tuple(sorted([a[0], b[0]]))
        if key not in used:
            used.add(key)
            candidates.append((a, b))
            break
    else:
        a, b = random.sample(books, 2)
        candidates.append((a, b))

for i, (a, b) in enumerate(candidates, 1):
    print(f'--- CANDIDATE {i} ---')
    print(f'A: {a[0]} | {a[1]}')
    print(f'B: {b[0]} | {b[1]}')
