#!/usr/bin/env python3
"""Read R2 books.json -> max id, all slugs, recent entries."""
import json, os, boto3
from botocore.config import Config

# parse .env manually (avoid dotenv issues)
env = {}
for line in open('/root/novel-site/.env'):
    line = line.strip()
    if not line or line.startswith('#') or '=' not in line:
        continue
    k, v = line.split('=', 1)
    env[k.strip()] = v.strip().strip('"').strip("'")

s3 = boto3.client('s3', endpoint_url=env['R2_ENDPOINT'],
                  aws_access_key_id=env['R2_ACCESS_KEY_ID'],
                  aws_secret_access_key=env['R2_SECRET_ACCESS_KEY'],
                  config=Config(signature_version='s3v4'), region_name='auto')
obj = s3.get_object(Bucket=env.get('R2_BUCKET', 'novel-data'), Key='books.json')
books = json.loads(obj['Body'].read().decode())
if isinstance(books, dict):
    books = books.get('books', books.get('data', []))
ids = [b.get('id') for b in books if isinstance(b.get('id'), int)]
print("count:", len(books), "max_id:", max(ids))
slugs = sorted({b.get('slug') for b in books if b.get('slug')})
print("slugs:", len(slugs))
json.dump(slugs, open('/root/novels/_factory_slugs.json', 'w'))
print("last 5:", [(b.get('id'), b.get('slug'), b.get('title')) for b in books[-5:]])
