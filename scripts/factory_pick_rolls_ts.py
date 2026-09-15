#!/usr/bin/env python3
"""Cron factory: 5 rolls of random classic pairs, timestamp-based seeds."""
import random, re, sys, datetime

base = int(datetime.datetime.now().timestamp())

with open('/root/世界名著大全.md', encoding='utf-8') as f:
    text = f.read()

uniq = []
seen = set()
for m in re.finditer(r'《([^》]+)》\s*\|\s*([^\n|]+)', text):
    t, a = m.group(1).strip(), m.group(2).strip()
    if t not in seen:
        seen.add(t)
        uniq.append((t, a))

print(f"base_seed={base} total_entries={len(uniq)}")
print("--- 5 rolls (pair | authors) ---")
for r in range(5):
    random.seed(base + r * 7919 + 1)
    i1, i2 = random.sample(range(len(uniq)), 2)
    print(f"roll{r+1}: 《{uniq[i1][0]}》 | {uniq[i1][1]}  x  《{uniq[i2][0]}》 | {uniq[i2][1]}")
