#!/usr/bin/env python3
"""Phase 1: pick classic pairs with timestamp seed; dump R2 state (max id, slugs)."""
import re, json, random, os, sys
from datetime import datetime

# --- 1. Parse classics ---
text = open('/root/世界名著大全.md', encoding='utf-8').read()
rows = re.findall(r'《([^》]+)》\s*\|\s*([^|\n]+)', text)
if not rows:
    rows = [(m, '') for m in re.findall(r'《([^》]+)》', text)]
print(f"parsed classics: {len(rows)}")

# --- 2. R2 state: max id + existing slugs ---
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
print(f"books.json entries: {len(books)}")
ids = sorted(int(b['id']) for b in books)
maxid = max(ids)
slugs = set(b.get('slug') for b in books)
print(f"max id: {maxid}")
print(f"slugs: {len(slugs)}")

# --- 3. Pick 4 candidate pairs, seed = current timestamp ---
seed = int(sys.argv[1]) if len(sys.argv) > 1 else int(datetime.now().timestamp())
print(f"seed: {seed}")
rng = random.Random(seed)
# sample without replacement to avoid dup within run
idx = rng.sample(range(len(rows)), 8)
pairs = [(rows[idx[2*i]], rows[idx[2*i+1]]) for i in range(4)]
for i, (a, b) in enumerate(pairs):
    print(f"pair{i+1}: 《{a[0]}》(by {a[1]})  x  《{b[0]}》(by {b[1]})")

# slug collision check for candidate titles
print("--- slug collisions (candidate titles) ---")
for i, (a, b) in enumerate(pairs):
    for t, tag in [(a[0], 'a'), (b[0], 'b')]:
        slug = re.sub(r'[^a-z0-9]+', '-', t.lower()).strip('-')
        if slug in slugs:
            print(f"pair{i+1} {tag}: '{slug}' ALREADY EXISTS")
