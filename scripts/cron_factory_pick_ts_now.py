#!/usr/bin/env python3
"""Pick candidate classic pairs with timestamp seed (cron factory Phase 1)."""
import random, re, sys

src = "/root/世界名著大全.md"
text = open(src, encoding="utf-8").read()
titles = re.findall(r"《([^》]+)》\s*\|\s*([^|\n]+)", text)
titles = [(t.strip(), a.strip()) for t, a in titles if t.strip() and a.strip()]
print(f"parsed {len(titles)} classics", file=sys.stderr)

seed = int(sys.argv[1]) if len(sys.argv) > 1 else int(__import__("time").time())
random.seed(seed)
# sample 5 pairs (first is the primary; re-rolls are the rest)
pairs = []
used = set()
for _ in range(5):
    while True:
        i, j = random.sample(range(len(titles)), 2)
        if (i, j) not in used and (j, i) not in used:
            used.add((i, j))
            break
    pairs.append((titles[i], titles[j]))

for n, (a, b) in enumerate(pairs, 1):
    print(f"PAIR{n}: 《{a[0]}》 {a[1]}  ×  《{b[0]}》 {b[1]}")
