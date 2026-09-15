#!/usr/bin/env python3
"""Draw candidate classic pairs for fusion scoring. Seed = current timestamp."""
import random, re, sys

seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1789052467
text = open('/root/世界名著大全.md', encoding='utf-8').read()
titles = re.findall(r'《([^》]+)》', text)
titles = list(dict.fromkeys(titles))  # dedupe, keep order
print(f"TOTAL_CLASSICS={len(titles)}")

rng = random.Random(seed)
for attempt in range(5):
    pool = titles[:]
    rng.shuffle(pool)
    print(f"=== ATTEMPT {attempt+1} (seed={seed}+{attempt}) ===")
    for pi in range(4):
        a = pool[pi*2]
        b = pool[pi*2+1]
        print(f"PAIR {pi+1}: {a} × {b}")
    seed += 1
    rng = random.Random(seed)
