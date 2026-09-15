#!/usr/bin/env python3
"""Read back R2 state for id 1538: books.json entry + catalog count + spot-check chapter object."""
import json, os
import boto3
from dotenv import load_dotenv

load_dotenv('/root/novel-site/.env')
c = boto3.client('s3', endpoint_url=os.environ['R2_ENDPOINT'],
    aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'])
bucket = os.environ['R2_BUCKET']

books = json.loads(c.get_object(Bucket=bucket, Key='books.json')['Body'].read())
items = books if isinstance(books, list) else books.get('books', [])
entry = next((b for b in items if isinstance(b, dict) and b.get('id') == 1538), None)
print('entry:', json.dumps({k: entry.get(k) for k in ('id', 'title', 'slug', 'lang', 'total_chapters', 'author')} if entry else None, ensure_ascii=False))

cat = json.loads(c.get_object(Bucket=bucket, Key='catalog_1538.json')['Body'].read())
print('catalog_count:', len(cat) if isinstance(cat, list) else len(cat.get('chapters', [])))
first = cat[0] if isinstance(cat, list) else cat['chapters'][0]
print('first_entry_keys:', sorted(first.keys()))
print('first_chapter_id_type:', type(first.get('chapter_id')).__name__, first.get('chapter_id'))

ch1 = json.loads(c.get_object(Bucket=bucket, Key='1538/1.json')['Body'].read())
print('ch1 title:', ch1.get('title'))
print('ch1 has highlight:', bool(ch1.get('highlight')))
print('ch1 content_paras:', len(ch1.get('content', [])))
