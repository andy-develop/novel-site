#!/usr/bin/env python3
"""Query R2 books.json: max id, all slugs, count."""
import json, boto3

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
    aws_access_key_id=env['R2_ACCESS_KEY_ID'],
    aws_secret_access_key=env['R2_SECRET_ACCESS_KEY'])
obj = c.get_object(Bucket=env['R2_BUCKET'], Key='books.json')
books = json.loads(obj['Body'].read().decode())
print("total books:", len(books))
ids = sorted(b.get('id', 0) for b in books)
print("max id:", max(ids))
slugs = sorted(b.get('slug', '') for b in books)
print("slugs:", ",".join(slugs))
# show a sample entry structure
if books:
    sample = max(books, key=lambda b: b.get('id', 0))
    print("latest entry keys:", sorted(sample.keys()))
    print("latest:", json.dumps(sample, ensure_ascii=False)[:600])
