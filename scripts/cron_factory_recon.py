#!/usr/bin/env python3
"""Cron factory recon: R2 books.json -> max id, all slugs, newest entries."""
import json, os
env = {}
for line in open('/root/novel-site/.env', encoding='utf-8'):
    line = line.strip()
    if not line or line.startswith('#') or '=' not in line:
        continue
    k, v = line.split('=', 1)
    env[k] = v.strip().strip('"').strip("'")
import boto3
c = boto3.client('s3', endpoint_url=env['R2_ENDPOINT'],
    aws_access_key_id=env['R2_ACCESS_KEY_ID'],
    aws_secret_access_key=env['R2_SECRET_ACCESS_KEY'])
obj = c.get_object(Bucket=env['R2_BUCKET'], Key='books.json')
books = json.loads(obj['Body'].read().decode())
ids = sorted(b['id'] for b in books)
print("total books:", len(books))
print("max id:", max(ids))
print("ids tail:", ids[-8:])
print("all slugs:", sorted(b.get('slug','?') for b in books))
print("--- newest 6 ---")
for b in sorted(books, key=lambda x: x['id'])[-6:]:
    print(b['id'], b.get('slug'), '|', b.get('title'), '|', b.get('lang'), '|', b.get('total_chapters'), '|', b.get('category','')[:60], '|', b.get('tags'))
