#!/usr/bin/env python3
"""Pick 4 candidate classic pairs with timestamp seed."""
import re, random, time, sys

entries = []
with open('/root/世界名著大全.md', encoding='utf-8') as f:
    for line in f:
        m = re.search(r'《([^》]+)》\s*\|\s*([^|]+?)\s*\|', line)
        if m:
            entries.append((m.group(1).strip(), m.group(2).strip()))
print("parsed entries:", len(entries))

seed = int(time.time())
print("seed:", seed)
random.seed(seed)

pairs = []
seen = set()
while len(pairs) < 4:
    a, b = random.sample(entries, 2)
    key = tuple(sorted([a[0], b[0]]))
    if key in seen:
        continue
    seen.add(key)
    pairs.append((a, b))

out = []
for i, (a, b) in enumerate(pairs, 1):
    out.append(f"PAIR {i}: 《{a[0]}》({a[1]}) x 《{b[0]}》({b[1]})")
    print(out[-1])
with open('/tmp/cron_pairs.txt', 'w', encoding='utf-8') as f:
    f.write("\n".join(out))
