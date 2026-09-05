#!/usr/bin/env python3
"""Independent R2 read-back verification for book 1352."""
import boto3, json

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
b = env['R2_BUCKET']

books = json.loads(c.get_object(Bucket=b, Key='books.json')['Body'].read())
entry = [x for x in books if x.get('id') == 1352]
print("books.json entry:", json.dumps(entry[0], ensure_ascii=False) if entry else "MISSING")

cat = json.loads(c.get_object(Bucket=b, Key='catalog_1352.json')['Body'].read())
print("catalog chapters:", len(cat['chapters']))
print("chapter_id types ok:", all(isinstance(x['chapter_id'], int) for x in cat['chapters']))
print("first/last catalog titles:", cat['chapters'][0]['title'], "|", cat['chapters'][-1]['title'])

for n in [1, 13, 26]:
    obj = json.loads(c.get_object(Bucket=b, Key=f'1352/{n}.json')['Body'].read())
    print(f"ch{n}: id={obj['chapter_id']} title={obj['title'][:40]!r} paras={len(obj['content'])} highlight={bool(obj.get('highlight'))} hl={obj.get('highlight','')[:60]!r}")
