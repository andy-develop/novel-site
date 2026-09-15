#!/usr/bin/env python3
"""Pick 4 candidate classic pairs with a timestamp seed."""
import re, random, time, json, sys

ts = int(time.time())
random.seed(ts)
text = open('/root/世界名著大全.md', encoding='utf-8').read()
titles = re.findall(r'《([^》]+)》', text)
# dedupe preserving order
seen = set(); uniq = []
for t in titles:
    t = t.strip()
    if t and t not in seen:
        seen.add(t); uniq.append(t)
print("total classics:", len(uniq))
pairs = []
for i in range(4):
    a, b = random.sample(uniq, 2)
    pairs.append([a, b])
out = {"ts": ts, "total": len(uniq), "pairs": pairs}
json.dump(out, open('/root/novels/_factory_pairs_ts.json', 'w'), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
