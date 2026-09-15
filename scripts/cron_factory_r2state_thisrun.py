#!/usr/bin/env python3
"""Fetch R2 books.json: print max id, slug list, and recent titles (for slug-collision avoidance)."""
import os, json, boto3

def load_env(path):
    env = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env

env = load_env('/root/novel-site/.env')
client = boto3.client('s3', endpoint_url=env['R2_ENDPOINT'],
    aws_access_key_id=env['R2_ACCESS_KEY_ID'], aws_secret_access_key=env['R2_SECRET_ACCESS_KEY'])
obj = client.get_object(Bucket=env['R2_BUCKET'], Key='books.json')
books = json.loads(obj['Body'].read().decode('utf-8'))
max_id = max(b['id'] for b in books)
slugs = sorted(b['slug'] for b in books)
print('COUNT', len(books))
print('MAX_ID', max_id)
print('SLUGS', ','.join(slugs))
print('RECENT')
for b in sorted(books, key=lambda x: -x['id'])[:15]:
    print(b['id'], '|', b.get('slug'), '|', b.get('title'), '|', b.get('lang'), '|', b.get('total_chapters'))
