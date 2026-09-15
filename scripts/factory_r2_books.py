#!/usr/bin/env python3
"""Read R2 books.json: print max id, all slugs, count, lang counts."""
import os, json, sys
from dotenv import load_dotenv
load_dotenv('/root/novel-site/.env')
import boto3

s3 = boto3.client('s3', endpoint_url=os.environ['R2_ENDPOINT'],
                  aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
                  aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'],
                  region_name='auto')
try:
    obj = s3.get_object(Bucket=os.environ['R2_BUCKET'], Key='books.json')
    books = json.loads(obj['Body'].read().decode('utf-8'))
except s3.exceptions.NoSuchKey:
    books = []

ids = [b.get('id') for b in books if isinstance(b.get('id'), int)]
max_id = max(ids) if ids else 0
print(f"TOTAL_BOOKS={len(books)}")
print(f"MAX_ID={max_id}")
slugs = sorted(b.get('slug','') for b in books)
print("SLUGS:")
for s in slugs:
    print(" ", s)
langs = {}
for b in books:
    l = b.get('lang') or 'none'
    langs[l] = langs.get(l, 0) + 1
print("LANGS:", langs)
# latest 5 books by id
latest = sorted(books, key=lambda b: b.get('id',0))[-5:]
print("LATEST5:")
for b in latest:
    print(f"  id={b.get('id')} slug={b.get('slug')} title={b.get('title')} ch={b.get('total_chapters')} lang={b.get('lang')}")
