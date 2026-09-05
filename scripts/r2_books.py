#!/usr/bin/env python3
"""Query R2 books.json: max id, slugs, langs."""
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
ids = sorted(b['id'] for b in books)
print("total books:", len(books))
print("max id:", max(ids))
print("ids tail:", ids[-8:])
print("slugs:", sorted(b.get('slug','') for b in books))
langs = {}
for b in books:
    langs[b.get('lang','?')] = langs.get(b.get('lang','?'), 0) + 1
print("langs:", langs)
if '--json' in sys.argv:
    print("JSON:", json.dumps(books, ensure_ascii=False))
