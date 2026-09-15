#!/usr/bin/env python3
"""Cron factory recon: max book id + existing slugs from R2 books.json."""
import boto3, json, sys
from botocore.config import Config

env = {}
for line in open('/root/novel-site/.env', encoding='utf-8'):
    line = line.strip()
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        env[k.strip()] = v.strip().strip('"').strip("'")

s3 = boto3.client(
    's3',
    endpoint_url=env.get('R2_ENDPOINT'),
    aws_access_key_id=env.get('R2_ACCESS_KEY_ID'),
    aws_secret_access_key=env.get('R2_SECRET_ACCESS_KEY'),
    config=Config(signature_version='s3v4'),
    region_name='auto',
)
bucket = env.get('R2_BUCKET', 'novel-data')
obj = s3.get_object(Bucket=bucket, Key='books.json')
books = json.loads(obj['Body'].read().decode('utf-8'))
if isinstance(books, dict):
    books = books.get('books', books.get('data', []))
ids = [b.get('id') for b in books if isinstance(b, dict) and b.get('id') is not None]
print('MAX_ID:', max(ids) if ids else 0)
print('COUNT:', len(books))
slugs = sorted(b.get('slug', '') for b in books if isinstance(b, dict))
print('SLUGS:', ','.join(slugs))
for b in books:
    if isinstance(b, dict) and b.get('slug') in ('delusion-girl', 'legacy-girl'):
        print('COLLISION:', json.dumps(b, ensure_ascii=False)[:300])
