#!/usr/bin/env python3
"""Sample 5 random classic pairs with timestamp seed (cron factory Phase 1)."""
import random, re, json, time

with open('/root/世界名著大全.md', encoding='utf-8') as f:
    text = f.read()

entries = re.findall(r'《([^》]+)》\s*\|\s*([^\n|]+)', text)
seen = []
for title, author in entries:
    author = author.strip()
    if title not in [s[0] for s in seen]:
        seen.append((title, author))

print(f'parsed {len(seen)} unique classics')

seed = int(time.time())
random.seed(seed)
print(f'seed: {seed}')

pairs = []
for i in range(5):
    a, b = random.sample(seen, 2)
    pairs.append((a, b))

for i, (a, b) in enumerate(pairs, 1):
    print(f'PAIR{i}: 《{a[0]}》/{a[1]}  ×  《{b[0]}》/{b[1]}')

with open('/tmp/factory_pairs.json', 'w', encoding='utf-8') as f:
    json.dump([[list(a), list(b)] for a, b in pairs], f, ensure_ascii=False)
