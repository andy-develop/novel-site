#!/usr/bin/env python3
"""Verify R2 objects for book 1545: catalog chapter_id type, highlight presence."""
import boto3, json, os
from dotenv import load_dotenv
load_dotenv('/root/novel-site/.env')
s3 = boto3.client('s3', endpoint_url=os.environ['R2_ENDPOINT'],
                  aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
                  aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'], region_name='auto')
B = os.environ['R2_BUCKET']
cat = json.loads(s3.get_object(Bucket=B, Key='catalog_1545.json')['Body'].read())
chs = cat.get('chapters', cat if isinstance(cat, list) else [])
print('catalog chapters:', len(chs))
types = set(type(c.get('chapter_id')).__name__ for c in chs)
print('chapter_id types:', types)
bad = [c for c in chs if c.get('chapter_id') is None]
print('missing chapter_id:', len(bad))
books = json.loads(s3.get_object(Bucket=B, Key='books.json')['Body'].read())
entry = [b for b in books if b.get('id') == 1545]
print('books entry:', json.dumps(entry[0], ensure_ascii=False)[:400] if entry else 'MISSING')
# spot check chapter objects for highlight
for n in (1, 15, 30):
    obj = json.loads(s3.get_object(Bucket=B, Key=f'1545/{n}.json')['Body'].read())
    print(f'ch{n}: keys={sorted(obj.keys())} hl={bool(obj.get("highlight"))} title={obj.get("title")[:45]}')
