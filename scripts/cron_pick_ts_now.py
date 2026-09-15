import re, random, json

seed = int(open('/tmp/factory_seed.txt').read().strip())
random.seed(seed)

titles = []
with open('/root/世界名著大全.md') as f:
    for line in f:
        for m in re.findall(r'《([^》]+)》', line):
            titles.append(m)

print('total titles:', len(titles))

def pick_pair(seed_off):
    r = random.Random(seed + seed_off)
    return r.sample(titles, 2)

for i in range(5):
    p = pick_pair(i)
    print(f'pair {i}: {p[0]} × {p[1]}')
