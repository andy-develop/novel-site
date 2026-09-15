#!/usr/bin/env python3
"""Phase 1: parse classics list, seed with timestamp, sample candidate pairs."""
import random, re, sys

seed = int(sys.argv[1]) if len(sys.argv) > 1 else int(open('/dev/urandom', 'rb').read(4).hex(), 16)
text = open('/root/世界名著大全.md', encoding='utf-8').read()
books = re.findall(r'《([^》]+)》', text)
books = list(dict.fromkeys(books))  # dedupe preserve order
print('TOTAL_UNIQUE:', len(books))

random.seed(seed)
titles = set()
attempts = int(sys.argv[2]) if len(sys.argv) > 2 else 5
for a in range(attempts):
    pairs = []
    for _ in range(4):
        b1, b2 = random.sample(books, 2)
        key = tuple(sorted([b1, b2]))
        while key in titles:
            b1, b2 = random.sample(books, 2)
            key = tuple(sorted([b1, b2]))
        titles.add(key)
        pairs.append((b1, b2))
    print(f'=== ATTEMPT {a+1} ===')
    for i, (b1, b2) in enumerate(pairs, 1):
        print(f'PAIR {i}: {b1} | {b2}')
    if a < attempts - 1:
        print('---')
