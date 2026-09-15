#!/usr/bin/env python3
"""Verify R2 objects for book 1483 (Delusion Girl)."""
import boto3, json
from botocore.config import Config

env = {}
for line in open('/root/novel-site/.env', encoding='utf-8'):
    line = line.strip()
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        env[k.strip()] = v.strip().strip('"').strip("'")

s3 = boto3.client('s3', endpoint_url=env.get('R2_ENDPOINT'),
                  aws_access_key_id=env.get('R2_ACCESS_KEY_ID'),
                  aws_secret_access_key=env.get('R2_SECRET_ACCESS_KEY'),
                  config=Config(signature_version='s3v4'), region_name='auto')
B = env.get('R2_BUCKET', 'novel-data')

books = json.loads(s3.get_object(Bucket=B, Key='books.json')['Body'].read())
if isinstance(books, dict):
    books = books.get('books', books.get('data', []))
entry = [b for b in books if isinstance(b, dict) and b.get('id') == 1483]
print('books.json entry:', json.dumps(entry[0], ensure_ascii=False)[:400] if entry else 'MISSING')

cat = json.loads(s3.get_object(Bucket=B, Key='catalog_1483.json')['Body'].read())
chapters = cat.get('chapters', cat) if isinstance(cat, dict) else cat
print('catalog chapters:', len(chapters), '| first keys:', sorted(chapters[0].keys())[:8] if chapters else None)
print('chapter_id types:', set(type(c.get('chapter_id')).__name__ for c in chapters[:35]))

hl_ok = 0; hl_missing = []
for c in chapters:
    ch = s3.get_object(Bucket=B, Key=f'1483/{c["chapter_id"]}.json')['Body'].read()
    obj = json.loads(ch)
    if obj.get('highlight') and len(str(obj.get('highlight'))) > 5:
        hl_ok += 1
    else:
        hl_missing.append(c.get('chapter_id'))
print(f'highlights ok: {hl_ok}/{len(chapters)}', 'missing:', hl_missing[:10] if hl_missing else 'none')
