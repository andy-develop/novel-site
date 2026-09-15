#!/usr/bin/env python3
"""Show 3 sample book entries (category/tags/intro conventions) from R2 books.json."""
import json, boto3

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
                      aws_access_key_id=env['R2_ACCESS_KEY_ID'],
                      aws_secret_access_key=env['R2_SECRET_ACCESS_KEY'])
books = json.loads(client.get_object(Bucket=env['R2_BUCKET'], Key='books.json')['Body'].read())
for b in books[-4:]:
    print(json.dumps({k: b.get(k) for k in ['id', 'slug', 'title', 'author', 'category', 'lang', 'total_chapters', 'tags']}, ensure_ascii=False))
    print('  intro:', (b.get('intro') or '')[:90])
