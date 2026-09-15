#!/usr/bin/env python3
"""Check R2 state: max book id, total books, all slugs, langs."""
import boto3, json, os

env = {}
for line in open('/root/novel-site/.env', encoding='utf-8'):
    line = line.strip()
    if not line or line.startswith('#') or '=' not in line:
        continue
    k, v = line.split('=', 1)
    env[k] = v.strip().strip('"').strip("'")

client = boto3.client('s3', endpoint_url=env['R2_ENDPOINT'],
    aws_access_key_id=env['R2_ACCESS_KEY_ID'],
    aws_secret_access_key=env['R2_SECRET_ACCESS_KEY'])
obj = client.get_object(Bucket=env['R2_BUCKET'], Key='books.json')
books = json.loads(obj['Body'].read().decode())
ids = [b['id'] for b in books]
print("count:", len(books))
print("max_id:", max(ids))
print("recent_ids:", sorted(ids)[-8:])
slugs = sorted(b.get('slug','') for b in books)
print("slugs_tail:", slugs[-25:])
eng = [b for b in books if b.get('lang') in ('english','en')]
print("english_count:", len(eng))
print("latest_english:", [(b['id'], b['slug']) for b in sorted(eng, key=lambda x: x['id'])[-6:]])
# check for duplicate slugs
from collections import Counter
dup = [s for s,c in Counter(b.get('slug','') for b in books).items() if c>1]
print("dup_slugs:", dup)
