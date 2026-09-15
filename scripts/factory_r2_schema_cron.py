#!/usr/bin/env python3
"""Inspect books.json schema: keys of last entries + real id field."""
import json, boto3
from botocore.config import Config

env = {}
with open('/root/novel-site/.env') as f:
    for line in f:
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            env[k] = v.strip().strip('"').strip("'")

s3 = boto3.client('s3', endpoint_url=env['R2_ENDPOINT'], aws_access_key_id=env['R2_ACCESS_KEY_ID'],
                  aws_secret_access_key=env['R2_SECRET_ACCESS_KEY'], config=Config(signature_version='s3v4'),
                  region_name='auto')
obj = s3.get_object(Bucket=env['R2_BUCKET'], Key='books.json')
books = json.loads(obj['Body'].read().decode())
print('count:', len(books))
print('keys of first book:', list(books[0].keys()))
# find any numeric id field
for field in ('book_id', 'id', 'bookId'):
    vals = [b.get(field) for b in books[:20]]
    print(field, '->', vals[:8])
# numeric candidates
nums = [b for b in books if isinstance(b.get('id'), int)]
print('books with int id:', len(nums))
ids = sorted(b.get('id') for b in nums)
print('max int id:', ids[-1] if ids else None)
last = books[-3:]
for b in last:
    print(json.dumps({k: b.get(k) for k in ('id', 'book_id', 'slug', 'title', 'lang', 'total_chapters', 'genre', 'tags')}, ensure_ascii=False))
