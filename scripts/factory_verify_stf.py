#!/usr/bin/env python3
"""Verify books.json entry for book id 1465 + catalog shape."""
import json, os, sys
os.chdir('/root/novel-site')
from dotenv import load_dotenv
load_dotenv('/root/novel-site/.env')
import boto3
from botocore.config import Config

s3 = boto3.client('s3', endpoint_url=os.environ['R2_ENDPOINT'],
                  aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
                  aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'],
                  config=Config(signature_version='s3v4'), region_name='auto')
books = json.loads(s3.get_object(Bucket=os.environ['R2_BUCKET'], Key='books.json')['Body'].read())
books = books if isinstance(books, list) else books.get('books', [])
b = next((x for x in books if x.get('id') == 1465), None)
if not b:
    print("BOOK 1465 NOT FOUND"); sys.exit(1)
print(json.dumps({k: b.get(k) for k in ('id', 'slug', 'title', 'lang', 'total_chapters', 'category', 'tags')}, ensure_ascii=False))
cat = json.loads(s3.get_object(Bucket=os.environ['R2_BUCKET'], Key=f'catalog_1465.json')['Body'].read())
chs = cat.get('chapters', cat if isinstance(cat, list) else [])
print("catalog chapters:", len(chs))
print("first entry:", json.dumps(chs[0], ensure_ascii=False)[:200])
types = set(type(c.get('chapter_id')).__name__ for c in chs if isinstance(c, dict))
print("chapter_id types:", types)
hl = sum(1 for c in chs if c.get('highlight'))
print("chapters with highlight:", hl)
