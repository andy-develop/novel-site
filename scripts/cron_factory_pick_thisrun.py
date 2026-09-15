#!/usr/bin/env python3
"""Phase 1: sample classic pairs with time-based seed. Prints 6 candidate pairs."""
import re, random, sys

seed = int(sys.argv[1]) if len(sys.argv) > 1 else int(__import__('time').time())
text = open('/root/世界名著大全.md', encoding='utf-8').read()
titles = re.findall(r'《([^》]+)》', text)
# dedupe preserving order
seen = set(); classics = []
for t in titles:
    if t not in seen:
        seen.add(t); classics.append(t)
print('CLASSICS_COUNT', len(classics))
random.seed(seed)
# sample 10 distinct titles, form 5 pairs
titles_sample = random.sample(classics, 12)
pairs = []
for i in range(0, 12, 2):
    pairs.append((titles_sample[i], titles_sample[i+1]))
for idx, (a, b) in enumerate(pairs, 1):
    print(f'PAIR{idx}: 《{a}》 × 《{b}》')
