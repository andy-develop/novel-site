#!/usr/bin/env python3
"""Pick classic pairs with a timestamp seed for the novel factory. Prints pairs."""
import re, random, sys, os

path = "/root/世界名著大全.md"
seed = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.environ.get("TS", "0"))
text = open(path, encoding="utf-8").read()
titles = re.findall(r"《([^》]+)》", text)
titles = [t.strip() for t in titles if t.strip()]
titles = list(dict.fromkeys(titles))  # dedupe preserving order
print(f"parsed {len(titles)} unique titles", file=sys.stderr)

random.seed(seed)
pairs = []
used = set()
for _ in range(6):
    pool = [t for t in titles if t not in used]
    if len(pool) < 2:
        break
    a, b = random.sample(pool, 2)
    used.add(a); used.add(b)
    pairs.append((a, b))
for i, (a, b) in enumerate(pairs, 1):
    print(f"PAIR{i}: 《{a}》 × 《{b}》")
