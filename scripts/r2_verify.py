#!/usr/bin/env python3
"""Verify R2 objects for book 1457: books.json entry, catalog chapter_ids, chapter highlights."""
import boto3, json

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
bucket = env['R2_BUCKET']

books = json.loads(client.get_object(Bucket=bucket, Key='books.json')['Body'].read())
entry = next((b for b in books if b['id'] == 1457), None)
print('BOOKS_ENTRY:', json.dumps(entry, ensure_ascii=False)[:400] if entry else 'MISSING')

cat = json.loads(client.get_object(Bucket=bucket, Key='catalog_1457.json')['Body'].read())
chs = cat.get('chapters', [])
print('CATALOG_CHAPTERS:', len(chs))
ids_ok = all(isinstance(c.get('chapter_id'), int) for c in chs)
print('CHAPTER_IDS_INT:', ids_ok)
print('FIRST:', chs[0] if chs else None)
print('LAST:', chs[-1] if chs else None)

# sample chapter objects: 1, 15, 30
for n in (1, 15, 30):
    obj = json.loads(client.get_object(Bucket=bucket, Key=f'1457/{n}.json')['Body'].read())
    print(f'CH{n}: title={obj.get("title")!r} paras={len(obj.get("content", []))} highlight={bool(obj.get("highlight"))} hl={str(obj.get("highlight"))[:60]}')
