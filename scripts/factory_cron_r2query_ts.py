#!/usr/bin/env python3
"""Cron factory: read R2 books.json -> max id + existing slugs."""
import boto3, json, os
from dotenv import load_dotenv
load_dotenv('/root/novel-site/.env')

s3 = boto3.client('s3', endpoint_url=os.environ['R2_ENDPOINT'],
                  aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
                  aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'],
                  region_name='auto')
b = os.environ['R2_BUCKET']
try:
    obj = s3.get_object(Bucket=b, Key='books.json')
    books = json.loads(obj['Body'].read().decode('utf-8'))
except Exception as e:
    print("ERR", e); raise SystemExit(1)

maxid = 0
for bk in books:
    i = bk.get('id')
    if isinstance(i, int) and i > maxid:
        maxid = i
slugs = [bk.get('slug') for bk in books if bk.get('slug')]
print(f"total_books={len(books)} max_id={maxid}")
print("existing_slugs:")
for s in sorted(slugs):
    print(" ", s)
