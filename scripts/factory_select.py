#!/usr/bin/env python3
"""Phase 1: select 2 classics from 世界名著大全, score fusion. Seed = current timestamp."""
import re, random, sys, json

with open('/root/世界名著大全.md', encoding='utf-8') as f:
    text = f.read()

entries = re.findall(r'《([^》]+)》\s*\|\s*([^\n]+)', text)
entries = [(t.strip(), a.strip()) for t, a in entries]
# dedupe keeping order
seen = set()
uniq = []
for t, a in entries:
    if t not in seen:
        seen.add(t)
        uniq.append((t, a))
entries = uniq
print("total unique entries:", len(entries))

seed = int(sys.argv[1]) if len(sys.argv) > 1 else 42
rng = random.Random(seed)
idxs = rng.sample(range(len(entries)), 10)
pool = [entries[i] for i in idxs]
print("drawn 10 candidates:")
for t, a in pool:
    print(f"  {t} | {a}")
print("---POOL_JSON---")
print(json.dumps(pool, ensure_ascii=False))
