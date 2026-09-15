#!/usr/bin/env python3
"""Sample classic pairs using timestamp seed. Prints 4 candidate pairs."""
import random, re, sys

books = []
with open('/root/世界名著大全.md', encoding='utf-8') as f:
    for line in f:
        for m in re.finditer(r'《([^》]+)》\s*\|\s*([^|\s]+)', line):
            books.append((m.group(1).strip(), m.group(2).strip()))
        # also catch 《名》|作者 without space variations already covered

print('TOTAL_BOOKS', len(books), file=sys.stderr)

seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1789059661
rng = random.Random(seed)
# Shuffle a copy, then form 4 pairs from the front
pool = books[:]
rng.shuffle(pool)
for i in range(0, 8, 2):
    a, b = pool[i], pool[i+1]
    print(f'PAIR {i//2+1}: 《{a[0]}》 | {a[1]}  ×  《{b[0]}》 | {b[1]}')
