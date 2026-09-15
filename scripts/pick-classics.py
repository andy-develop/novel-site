#!/usr/bin/env python3
"""Phase 1: sample classic pairs for fusion scoring. Seed = current timestamp."""
import re, random, sys, time

text = open('/root/世界名著大全.md', encoding='utf-8').read()
entries = re.findall(r'《([^》]+)》\s*\|\s*([^\n|]+)', text)
print('entries found:', len(entries))

# dedupe by title
seen = set()
uniq = []
for t, a in entries:
    t = t.strip()
    a = a.strip()
    key = t.lower()
    if key in seen:
        continue
    seen.add(key)
    uniq.append((t, a))
print('unique:', len(uniq))

seed = int(sys.argv[1]) if len(sys.argv) > 1 else int(time.time())
random.seed(seed)
print('seed:', seed)

# Sample 5 pairs (avoid same-author pairs where possible)
pairs = []
attempt = 0
while len(pairs) < 5 and attempt < 200:
    attempt += 1
    a, b = random.sample(uniq, 2)
    if a[1] == b[1]:  # same author
        continue
    key = tuple(sorted([a[0], b[0]]))
    if key in {tuple(sorted([p[0], p[1]])) for p in pairs}:
        continue
    pairs.append((a, b))

for i, (a, b) in enumerate(pairs, 1):
    print(f"PAIR {i}: 《{a[0]}》 | {a[1]}  ×  《{b[0]}》 | {b[1]}")
