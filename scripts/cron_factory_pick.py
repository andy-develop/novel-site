#!/usr/bin/env python3
"""Cron factory Phase 1: pick 5 random classic pairs with timestamp seed."""
import random, re, sys, time

entries = []
for line in open('/root/世界名著大全.md', encoding='utf-8'):
    m = re.search(r'《([^》]+)》\s*\|\s*([^|]+)', line)
    if m:
        entries.append((m.group(1).strip(), m.group(2).strip()))
print(f"parsed {len(entries)} classics", file=sys.stderr)

seed = int(sys.argv[1]) if len(sys.argv) > 1 else int(time.time())
rng = random.Random(seed)
pool = entries[:]
rng.shuffle(pool)
for r in range(5):
    a = pool[2*r]
    b = pool[2*r+1]
    print(f"PAIR{r+1}: {a[0]} | {a[1]}  ×  {b[0]} | {b[1]}")
print(f"SEED: {seed}")
