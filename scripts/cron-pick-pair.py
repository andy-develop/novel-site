#!/usr/bin/env python3
"""Phase 1: sample classic pairs with a timestamp seed."""
import random, re, sys

text = open('/root/世界名著大全.md', encoding='utf-8').read()
books = []
for m in re.finditer(r'《([^》]+)》\s*\|\s*([^|\n]+)', text):
    books.append((m.group(1).strip(), m.group(2).strip()))
# dedupe keep order
seen = set()
uniq = []
for b in books:
    if b[0] not in seen:
        seen.add(b[0]); uniq.append(b)
books = uniq
print(f"parsed {len(books)} unique classics")

seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1789164064
rng = random.Random(seed)
for round_i in range(4):
    pair = rng.sample(books, 2)
    print(f"PAIR{round_i+1}: 《{pair[0][0]}》|{pair[0][1]}  x  《{pair[1][0]}》|{pair[1][1]}")
