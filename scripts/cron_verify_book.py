#!/usr/bin/env python3
"""Verify R2 objects for kiss-the-ring (id 1495): catalog keys, chapter objects, books.json."""
import json, boto3

env = {}
for line in open('/root/novel-site/.env', encoding='utf-8'):
    line = line.strip()
    if not line or line.startswith('#') or '=' not in line:
        continue
    k, v = line.split('=', 1)
    env[k] = v.strip().strip('"').strip("'")

c = boto3.client('s3', endpoint_url=env['R2_ENDPOINT'],
                 aws_access_key_id=env['R2_ACCESS_KEY_ID'],
                 aws_secret_access_key=env['R2_SECRET_ACCESS_KEY'])

cat = json.loads(c.get_object(Bucket=env['R2_BUCKET'], Key='catalog_1495.json')['Body'].read())
chs = cat.get('chapters') or cat.get('chapter_list') or []
print('catalog keys:', list(cat.keys()))
print('chapter count:', len(chs))
print('first entry:', json.dumps(chs[0])[:200])
print('last entry:', json.dumps(chs[-1])[:200])
types = set(type(x.get('chapter_id')).__name__ for x in chs)
print('chapter_id types:', types)

obj = c.get_object(Bucket=env['R2_BUCKET'], Key='1495/1.json')
ch1 = json.loads(obj['Body'].read())
print('ch1 keys:', list(ch1.keys()), '| title:', ch1.get('title'), '| hl:', (ch1.get('highlight') or '')[:60])

obj = c.get_object(Bucket=env['R2_BUCKET'], Key='1495/30.json')
ch30 = json.loads(obj['Body'].read())
print('ch30 title:', ch30.get('title'), '| hl:', (ch30.get('highlight') or '')[:60])

books = json.loads(c.get_object(Bucket=env['R2_BUCKET'], Key='books.json')['Body'].read())
b = [x for x in books if x.get('id') == 1495][0]
print('books.json entry:', json.dumps({k: b.get(k) for k in ('id', 'slug', 'title', 'lang', 'total_chapters', 'author')}))
