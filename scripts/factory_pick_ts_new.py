#!/usr/bin/env python3
"""Pick 4 candidate classic pairs using a timestamp seed (batch factory Phase 1)."""
import random, re, sys, json

seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1789034453
text = open('/root/世界名著大全.md', encoding='utf-8').read()
titles = re.findall(r'《([^》]+)》', text)
titles = list(dict.fromkeys(titles))
print(f"total titles: {len(titles)}", flush=True)

random.seed(seed)
pairs = []
for i in range(4):
    a, b = random.sample(titles, 2)
    pairs.append((a, b))
print(json.dumps(pairs, ensure_ascii=False, indent=1))
