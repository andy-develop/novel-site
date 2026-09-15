#!/usr/bin/env python3
"""Phase 1: random 2 classics from 世界名著大全.md, seed = current timestamp."""
import re, random, sys, time

SEED = int(sys.argv[1]) if len(sys.argv) > 1 else int(time.time())

with open('/root/世界名著大全.md', encoding='utf-8') as f:
    text = f.read()

entries = re.findall(r'《([^》]+)》\s*[|｜]\s*([^\n|｜]+)', text)
if not entries:
    # fallback: just titles
    titles = re.findall(r'《([^》]+)》', text)
    entries = [(t, '?') for t in titles]

print(f"SEED={SEED}  total_entries={len(entries)}")

random.seed(SEED)
pairs = []
for i in range(5):
    a, b = random.sample(entries, 2)
    pairs.append((a, b))
    print(f"pair{i+1}: 《{a[0]}》 {a[1]}  ×  《{b[0]}》 {b[1]}")

# Save pairs to file for downstream
with open('/root/novel-site/scripts/selected_pairs.txt', 'w', encoding='utf-8') as f:
    for i, (a, b) in enumerate(pairs):
        f.write(f"{i+1}\t{a[0]}\t{a[1]}\t{b[0]}\t{b[1]}\n")
print("saved selected_pairs.txt")
