#!/usr/bin/env python3
"""Read R2 books.json: max id + all existing slugs (read-only)."""
import os, sys, json
sys.path.insert(0, '/root/novel-site/scripts')
os.chdir('/root/novel-site')

def load_env(path):
    env = {}
    for line in open(path, encoding='utf-8'):
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        env[k] = v.strip().strip('"').strip("'")
    return env

env = load_env('/root/novel-site/.env')
import boto3
s3 = boto3.client(
    's3', endpoint_url=env['R2_ENDPOINT'],
    aws_access_key_id=env['R2_ACCESS_KEY_ID'],
    aws_secret_access_key=env['R2_SECRET_ACCESS_KEY'],
    region_name='auto',
)
obj = s3.get_object(Bucket=env['R2_BUCKET'], Key='books.json')
books = json.loads(obj['Body'].read().decode())
ids = [b.get('id') for b in books if isinstance(b.get('id'), int)]
slugs = [b.get('slug') for b in books if b.get('slug')]
maxid = max(ids) if ids else 0
print('total books:', len(books))
print('max id:', maxid)
print('slugs:', sorted(slugs))
