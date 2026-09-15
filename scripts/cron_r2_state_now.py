#!/usr/bin/env python3
"""Recon R2 novel-data: max id, all slugs, newest books. Run from /root/novel-site."""
import boto3, json, sys

env = {}
for line in open('/root/novel-site/.env', encoding='utf-8'):
    line = line.strip()
    if not line or line.startswith('#') or '=' not in line:
        continue
    k, v = line.split('=', 1)
    env[k] = v.strip().strip('"').strip("'")

s3 = boto3.client(
    's3',
    endpoint_url=env['R2_ENDPOINT'],
    aws_access_key_id=env['R2_ACCESS_KEY_ID'],
    aws_secret_access_key=env['R2_SECRET_ACCESS_KEY'],
    region_name='auto',
)
try:
    obj = s3.get_object(Bucket=env['R2_BUCKET'], Key='books.json')
    books = json.loads(obj['Body'].read().decode('utf-8'))
except Exception as e:
    print(f'ERROR reading books.json: {e}')
    sys.exit(1)

books = books if isinstance(books, list) else books.get('books', books.get('data', []))
max_id = max(b['id'] for b in books if isinstance(b.get('id'), int))
slugs = sorted(b.get('slug', '') for b in books)
print(f'MAX_ID={max_id}')
print(f'TOTAL_BOOKS={len(books)}')
print(f'SLUG_COUNT={len(slugs)}')
recent = sorted(books, key=lambda b: b.get('id', 0))[-8:]
for b in recent:
    print(f"  id={b.get('id')} slug={b.get('slug')} chapters={b.get('total_chapters')} title={b.get('title','')[:40]}")
print('ALL_SLUGS:')
print(json.dumps(slugs))
