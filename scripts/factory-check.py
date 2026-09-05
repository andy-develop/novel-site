#!/usr/bin/env python3
"""Factory helper: read R2 books.json, print max id, slugs, sample entry."""
import boto3, json

env = {}
with open('/root/novel-site/.env') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip().strip('"').strip("'")

s3 = boto3.client('s3', endpoint_url=env.get('R2_ENDPOINT'),
                  aws_access_key_id=env.get('R2_ACCESS_KEY_ID'),
                  aws_secret_access_key=env.get('R2_SECRET_ACCESS_KEY'),
                  region_name='auto')
bucket = env.get('R2_BUCKET', 'novel-data')
resp = s3.get_object(Bucket=bucket, Key='books.json')
books = json.loads(resp['Body'].read())
ids = sorted(int(b['id']) for b in books)
slugs = sorted(b.get('slug', '?') for b in books)
print("num books:", len(books))
print("max id:", max(ids))
print("next id:", max(ids) + 1)
print("slugs:", slugs)
print()
print(json.dumps(books[0], indent=1)[:900])
