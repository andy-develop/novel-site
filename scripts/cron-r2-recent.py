#!/usr/bin/env python3
"""List recent books + check for combo overlap."""
import json, os, boto3, re
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
c = boto3.client('s3', endpoint_url=env['R2_ENDPOINT'],
    aws_access_key_id=env['R2_ACCESS_KEY_ID'],
    aws_secret_access_key=env['R2_SECRET_ACCESS_KEY'])
rbooks = json.loads(c.get_object(Bucket=env['R2_BUCKET'], Key='books.json')['Body'].read())
byid = sorted(rbooks, key=lambda b: b.get('id', 0))
print("--- last 25 books (id | title | slug | tags) ---")
for b in byid[-25:]:
    tags = ','.join(b.get('tags', []) or [])[:60]
    print(f"{b.get('id')} | {b.get('title','')[:50]} | {b.get('slug')} | {tags}")
print()
kw = ['canterbury', 'tragedy', 'pilgrim', 'confession', 'gone', 'wind', 'venice', 'musketeer', 'blood']
for k in kw:
    hits = [b.get('slug') for b in rbooks if k in (b.get('slug','') + ' ' + (b.get('title','') or '')).lower()]
    print(k, '->', hits[:12])
