#!/usr/bin/env python3
"""Cron factory: read R2 books.json -> max id, next id, slugs, latest titles."""
import json, sys
sys.path.insert(0, '/root/novel-site/scripts')

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
c = boto3.client('s3', endpoint_url=env['R2_ENDPOINT'],
    aws_access_key_id=env['R2_ACCESS_KEY_ID'],
    aws_secret_access_key=env['R2_SECRET_ACCESS_KEY'])
obj = c.get_object(Bucket=env['R2_BUCKET'], Key='books.json')
books = json.loads(obj['Body'].read().decode())
ids = [b['id'] for b in books]
slugs = [b['slug'] for b in books]
print(f"count={len(books)} max_id={max(ids)} next_id={max(ids)+1}")
print("--- all slugs ---")
print(','.join(sorted(slugs)))
