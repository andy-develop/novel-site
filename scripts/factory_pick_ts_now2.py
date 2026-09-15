import re, random, datetime
text = open('/root/世界名著大全.md', encoding='utf-8').read()
entries = re.findall(r'《([^》]+)》\s*\|\s*([^\n|]+)', text)
seen = {}
for t, a in entries:
    t = t.strip()
    if t and t not in seen:
        seen[t] = a.strip()
titles = list(seen.keys())
print("TOTAL_UNIQUE", len(titles))
seed = int(datetime.datetime.now().timestamp())
random.seed(seed)
pool = titles[:]
random.shuffle(pool)
pairs = []
for i in range(0, min(len(pool), 14), 2):
    pairs.append((pool[i], pool[i+1]))
for i, (a, b) in enumerate(pairs):
    print(f"PAIR{i}: 《{a}》 × 《{b}》")
print("SEED", seed)
