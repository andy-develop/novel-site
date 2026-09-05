#!/usr/bin/env python3
"""Phase 1b: distinct candidate pairs per attempt."""
import re, random, sys

text = open("/root/世界名著大全.md", encoding="utf-8").read()
titles = re.findall(r'《([^》]+)》', text)
seen = set(); uniq = []
for t in titles:
    if t not in seen:
        seen.add(t); uniq.append(t)

base = int(sys.argv[1]) if len(sys.argv) > 1 else 1788570041
for attempt in range(1, 6):
    rng = random.Random(base + attempt * 104729)
    picks = rng.sample(uniq, 8)
    pairs = [(picks[0], picks[1]), (picks[2], picks[3]), (picks[4], picks[5]), (picks[6], picks[7])]
    print(f"=== attempt {attempt} ===")
    for i, (a, b) in enumerate(pairs, 1):
        print(f"  pair {i}: 《{a}》 × 《{b}》")
