#!/usr/bin/env python3
"""Read R2 books.json: max id, total books, slugs, recent ids."""
import json, os
import boto3

env = {}
with open('/root/novel-site/.env') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        env[k.strip()] = v.strip().strip('"').strip("'")

client = boto3.client('s3', endpoint_url=env['R2_ENDPOINT'],
    aws_access_key_id=env['R2_ACCESS_KEY_ID'],
    aws_secret_access_key=env['R2_SECRET_ACCESS_KEY'])

obj = client.get_object(Bucket=env['R2_BUCKET'], Key='books.json')
books = json.loads(obj['Body'].read().decode('utf-8'))
ids = [b['id'] for b in books]
ids_sorted = sorted(ids)
print("count:", len(books))
print("max_id:", max(ids_sorted))
print("min_id:", min(ids_sorted))
print("all_ids:", ids_sorted)
print("--- slugs (newest 40 by id) ---")
for b in sorted(books, key=lambda x: x['id'])[-40:]:
    print(b['id'], b.get('slug'), b.get('lang'), b.get('total_chapters'))
print("--- all slugs ---")
print([b.get('slug') for b in books])
