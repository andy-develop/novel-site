#!/usr/bin/env python3
"""Read R2 books.json, print id/slug/lang/total_chapters/title, max id."""
import json, os, sys

def load_env(path):
    env = {}
    try:
        for line in open(path):
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    except FileNotFoundError:
        print("ENV FILE NOT FOUND:", path)
    return env

env = load_env('/root/novel-site/.env')
try:
    import boto3
except ImportError:
    print("boto3 NOT INSTALLED")
    sys.exit(1)

s3 = boto3.client('s3',
    endpoint_url=env.get('R2_ENDPOINT'),
    aws_access_key_id=env.get('R2_ACCESS_KEY_ID'),
    aws_secret_access_key=env.get('R2_SECRET_ACCESS_KEY'),
    region_name='auto')
obj = s3.get_object(Bucket=env.get('R2_BUCKET'), Key='books.json')
books = json.loads(obj['Body'].read())
print("count:", len(books))
for b in sorted(books, key=lambda x: x.get('id', 0)):
    print(b.get('id'), '|', b.get('slug'), '|', b.get('lang'), '|', b.get('total_chapters'), '|', str(b.get('title'))[:60])
ids = [b.get('id') for b in books if isinstance(b.get('id'), int)]
print("MAX_ID:", max(ids) if ids else 0)
