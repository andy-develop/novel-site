#!/usr/bin/env python3
"""Sample classic pairs for fusion scoring, seeded by current timestamp."""
import re, random, sys
from pathlib import Path

text = Path('/root/世界名著大全.md').read_text(encoding='utf-8')
pairs = []
for line in text.splitlines():
    m = re.findall(r'《([^》]+)》', line)
    am = re.search(r'\|\s*([^|]+?)\s*\|\s*$', line)
    if m and am:
        pairs.append((m[0], am.group(1).strip()))
print(f"TOTAL={len(pairs)}")

seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1789221653
rng = random.Random(seed)
for attempt in range(5):
    rng = random.Random(seed + attempt * 7919)
    chosen = rng.sample(pairs, 8)
    print(f"\n=== ATTEMPT {attempt+1} (seed {seed + attempt*7919}) — pairs ===")
    for i in range(0, 8, 2):
        a, b = chosen[i], chosen[i+1]
        print(f"PAIR {i//2+1}: 《{a[0]}》 | {a[1]}  ×  《{b[0]}》 | {b[1]}")
