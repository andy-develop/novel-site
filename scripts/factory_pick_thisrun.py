#!/usr/bin/env python3
"""Pick 4 random classic pairs seeded by current timestamp, print for scoring."""
import re, random, sys, time

text = open('/root/世界名著大全.md', encoding='utf-8').read()
titles = []
for line in text.splitlines():
    m = re.search(r'《([^》]+)》\s*\|', line)
    if m:
        titles.append((m.group(1), line.split('|')[-1].strip()))
# dedupe by title
seen = set()
uniq = []
for t, a in titles:
    if t not in seen:
        seen.add(t)
        uniq.append((t, a))
print(f"parsed {len(uniq)} unique classics", file=sys.stderr)

seed = int(time.time())
rng = random.Random(seed)
print(f"seed={seed}")
for i in range(4):
    a, b = rng.sample(uniq, 2)
    print(f"PAIR{i+1}: {a[0]} | {a[1]}  x  {b[0]} | {b[1]}")
