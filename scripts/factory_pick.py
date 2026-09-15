#!/usr/bin/env python3
"""Phase 1: sample 4 candidate classic pairs, seed = current timestamp."""
import re, random, time

with open('/root/世界名著大全.md', encoding='utf-8') as f:
    text = f.read()
titles = re.findall(r'《([^》]+)》', text)
# dedupe keeping order
seen = set()
uniq = []
for t in titles:
    if t not in seen:
        seen.add(t)
        uniq.append(t)
print("unique classics:", len(uniq))

seed = int(time.time())
rng = random.Random(seed)
print("seed:", seed, flush=True)

pairs = []
used = set()
for i in range(4):
    a = rng.choice(uniq)
    while a in used:
        a = rng.choice(uniq)
    used.add(a)
    b = rng.choice(uniq)
    while b in used:
        b = rng.choice(uniq)
    used.add(b)
    pairs.append((a, b))

for i, (a, b) in enumerate(pairs):
    print(f"pair{i+1}: 《{a}》 × 《{b}》")
