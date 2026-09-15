#!/usr/bin/env python3
"""Parse /root/世界名著大全.md, seed with current timestamp, print 5 random candidate pairs."""
import re, random, sys

text = open('/root/世界名著大全.md', encoding='utf-8').read()
entries = re.findall(r'《([^》]+)》\s*\|\s*([^\n|]+)', text)
print('entries:', len(entries))

seed = int(sys.argv[1]) if len(sys.argv) > 1 else int(__import__('time').time())
random.seed(seed)
# draw 5 pairs (10 distinct classics)
chosen = random.sample(entries, 10)
for i in range(5):
    a, b = chosen[2*i], chosen[2*i+1]
    print(f'PAIR{i+1}: 《{a[0]}》 {a[1].strip()}  ×  《{b[0]}》 {b[1].strip()}')
