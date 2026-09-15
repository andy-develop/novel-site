import re, random, sys

with open('/root/世界名著大全.md', encoding='utf-8') as f:
    text = f.read()

titles = re.findall(r'《([^》]+)》', text)
print('total titles:', len(titles))

seed = 1788980423
rng = random.Random(seed)

# sample 5 candidate pairs
pairs = []
for i in range(5):
    a, b = rng.sample(titles, 2)
    pairs.append((a, b))

for i, (a, b) in enumerate(pairs, 1):
    print(f'PAIR{i}: 《{a}》 x 《{b}》')
