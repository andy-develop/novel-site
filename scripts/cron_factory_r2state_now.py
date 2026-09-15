#!/usr/bin/env python3
"""Cron factory: read R2 books.json, print max id + slugs + count."""
import json, os, sys
import boto3
from dotenv import load_dotenv

load_dotenv('/root/novel-site/.env')
s3 = boto3.client(
    's3',
    endpoint_url=os.environ['R2_ENDPOINT'],
    aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'],
    region_name='auto',
)
bucket = os.environ['R2_BUCKET']
try:
    obj = s3.get_object(Bucket=bucket, Key='books.json')
    books = json.loads(obj['Body'].read().decode('utf-8'))
except Exception as e:
    print('ERROR reading books.json:', e)
    sys.exit(1)

if isinstance(books, dict):
    items = books.get('books', books.get('data', []))
else:
    items = books
ids = [b.get('id') for b in items if isinstance(b, dict) and b.get('id') is not None]
maxid = max(ids) if ids else 0
slugs = sorted({b.get('slug') for b in items if isinstance(b, dict) and b.get('slug')})
print('total_books:', len(items))
print('max_id:', maxid)
print('slug_count:', len(slugs))
print('slugs:', ','.join(slugs))
