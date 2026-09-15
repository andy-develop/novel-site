#!/usr/bin/env python3
"""Phase 1: pick classic pairs with timestamp seed; dump R2 state (max id, slugs)."""
import re, json, random, os
from datetime import datetime

SEED = int(os.environ.get('FACTORY_SEED', str(int(datetime.now().timestamp()))))
text = open('/root/世界名著大全.md', encoding='utf-8').read()
rows = re.findall(r'《([^》]+)》\s*\|?\s*([^|\n]*)', text)
if not rows:
    rows = [(m, '') for m in re.findall(r'《([^》]+)》', text)]
print(f"parsed classics: {len(rows)} seed={SEED}")

# R2 state
env = {}
for line in open('/root/novel-site/.env', encoding='utf-8'):
    line = line.strip()
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        env[k] = v.strip().strip('"').strip("'")
import boto3
s3 = boto3.client('s3', endpoint_url=env.get('R2_ENDPOINT'),
                  aws_access_key_id=env.get('R2_ACCESS_KEY_ID'),
                  aws_secret_access_key=env.get('R2_SECRET_ACCESS_KEY'),
                  region_name='auto')
obj = s3.get_object(Bucket=env.get('R2_BUCKET', 'novel-data'), Key='books.json')
books = json.loads(obj['Body'].read().decode('utf-8'))
ids = sorted(int(b['id']) for b in books)
slugs = set(b.get('slug') for b in books)
print(f"books entries={len(books)} max_id={ids[-1]} next_id={ids[-1]+1}")
print("slugs:")
for s in sorted(slugs):
    print(" ", s)

# sample 4 pairs with seed
rng = random.Random(SEED)
pairs = []
seen = set()
while len(pairs) < 4:
    i, j = rng.sample(range(len(rows)), 2)
    key = tuple(sorted((rows[i][0], rows[j][0])))
    if key in seen:
        continue
    seen.add(key)
    pairs.append((rows[i], rows[j]))
print("\nCANDIDATE PAIRS (seed %d):" % SEED)
for n, (a, b) in enumerate(pairs, 1):
    print(f"PAIR{n}: 《{a[0]}》|{a[1]}  x  《{b[0]}》|{b[1]}")
