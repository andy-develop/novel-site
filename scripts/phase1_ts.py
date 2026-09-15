#!/usr/bin/env python3
"""Phase 1: sample classic pairs with a seed, print for human scoring."""
import random, re, sys, json

seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1789020043
text = open('/root/世界名著大全.md', encoding='utf-8').read()
# entries like 《书名》 | 作者
pairs = re.findall(r'《([^》]+)》\s*\|\s*([^\n|]+)', text)
titles = [p[0] for p in pairs]
print(f"parsed {len(titles)} classics")

random.seed(seed)
candidates = []
seen = set()
while len(candidates) < 4:
    a, b = random.sample(titles, 2)
    key = tuple(sorted([a, b]))
    if key in seen:
        continue
    seen.add(key)
    candidates.append((a, b))
for i, (a, b) in enumerate(candidates, 1):
    print(f"PAIR {i}: 《{a}》 × 《{b}》")
json.dump(candidates, open('/root/novel-site/scripts/candidates_ts.json', 'w'), ensure_ascii=False)
