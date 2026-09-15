#!/usr/bin/env python3
"""Phase 1: sample 5 classic pairs from 世界名著大全.md with timestamp seed."""
import random, re, sys

seed = int(sys.argv[1]) if len(sys.argv) > 1 else int(__import__('time').time())
text = open('/root/世界名著大全.md', encoding='utf-8').read()
titles = re.findall(r'《([^》]+)》', text)
titles = [t.strip() for t in titles if t.strip()]
# dedupe preserving order
seen, uniq = set(), []
for t in titles:
    if t not in seen:
        seen.add(t)
        uniq.append(t)
titles = uniq
print(f'seed={seed} unique_classics={len(titles)}')

rng = random.Random(seed)
for i in range(5):
    a, b = rng.sample(titles, 2)
    # find authors by scanning lines
    def find_author(title):
        for line in text.splitlines():
            if f'《{title}》' in line:
                m = re.search(r'《[^》]+》\s*\|\s*([^|]+)$', line.strip())
                if m:
                    return m.group(1).strip()
        return '?'
    print(f'pair{i+1}: 《{a}》|{find_author(a)}  ×  《{b}》|{find_author(b)}')
