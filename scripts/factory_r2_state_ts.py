#!/usr/bin/env python3
"""Read R2 books.json: max id, all slugs, count. Cron-safe (no execute_code)."""
import boto3, json, os

env = {}
for line in open('/root/novel-site/.env', encoding='utf-8'):
    line = line.strip()
    if not line or line.startswith('#') or '=' not in line:
        continue
    k, v = line.split('=', 1)
    env[k] = v.strip().strip('"').strip("'")

s3 = boto3.client(
    's3',
    endpoint_url=env.get('R2_ENDPOINT'),
    aws_access_key_id=env.get('R2_ACCESS_KEY_ID'),
    aws_secret_access_key=env.get('R2_SECRET_ACCESS_KEY'),
    region_name='auto',
)
try:
    obj = s3.get_object(Bucket=env.get('R2_BUCKET', 'novel-data'), Key='books.json')
    books = json.loads(obj['Body'].read().decode('utf-8'))
    ids = [b.get('id') for b in books if isinstance(b.get('id'), int)]
    print('total_books:', len(books))
    print('max_id:', max(ids) if ids else 0)
    slugs = sorted(b.get('slug', '') for b in books if b.get('slug'))
    print('slug_count:', len(slugs))
    print('slugs:', ','.join(slugs))
except Exception as e:
    print('ERROR:', e)
