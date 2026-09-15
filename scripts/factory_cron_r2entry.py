#!/usr/bin/env python3
"""Verify books.json entry for a book id."""
import boto3, json, sys

def load_env(path):
    env = {}
    for line in open(path, encoding='utf-8'):
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        env[k] = v.strip().strip('"').strip("'")
    return env

env = load_env("/root/novel-site/.env")
c = boto3.client('s3', endpoint_url=env['R2_ENDPOINT'],
    aws_access_key_id=env['R2_ACCESS_KEY_ID'], aws_secret_access_key=env['R2_SECRET_ACCESS_KEY'])
books = json.loads(c.get_object(Bucket=env['R2_BUCKET'], Key='books.json')['Body'].read())
bid = int(sys.argv[1])
entry = [b for b in books if b.get('id') == bid]
print(json.dumps(entry, ensure_ascii=False, indent=1) if entry else "NOT FOUND")
cat = json.loads(c.get_object(Bucket=env['R2_BUCKET'], Key=f'catalog_{bid}.json')['Body'].read())
print("catalog chapters:", len(cat['chapters']), "| first:", cat['chapters'][0], "| last:", cat['chapters'][-1])
