import re, random, sys

text = open('/root/世界名著大全.md', encoding='utf-8').read()
pairs = re.findall(r'《([^》]+)》\s*\|\s*([^|\n]+)', text)
print('parsed classics:', len(pairs))

seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1789272014
rng = random.Random(seed)
# sample 4 candidate pairs (each pair = 2 distinct works, no repeats within pair)
cands = []
used = set()
for _ in range(20):
    i = rng.randrange(len(pairs)); j = rng.randrange(len(pairs))
    if i == j:
        continue
    a, b = pairs[i], pairs[j]
    key = tuple(sorted([a[0], b[0]]))
    if key in used:
        continue
    used.add(key)
    cands.append((a, b))
    if len(cands) >= 4:
        break
for n, (a, b) in enumerate(cands, 1):
    print(f'PAIR {n}: 《{a[0]}》/{a[1]}  x  《{b[0]}》/{b[1]}')
