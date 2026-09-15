#!/usr/bin/env python3
"""Cron-safe: read R2 books.json max id + slugs + catalog schema sample."""
import json, sys
from dotenv import load_dotenv
load_dotenv('/root/novel-site/.env')
import boto3, os

endpoint = os.environ['R2_ENDPOINT']
bucket = os.environ['R2_BUCKET']
key = os.environ['R2_ACCESS_KEY_ID']
secret = os.environ['R2_SECRET_ACCESS_KEY']

s3 = boto3.client('s3', endpoint_url=endpoint, aws_access_key_id=key,
                  aws_secret_access_key=secret, region_name='auto')
resp = s3.get_object(Bucket=bucket, Key='books.json')
books = json.loads(resp['Body'].read().decode('utf-8'))
print('total books:', len(books))
max_id = 0
for b in books:
    bid = b.get('id', b.get('book_id', 0))
    if isinstance(bid, int) and bid > max_id:
        max_id = bid
print('max id:', max_id)
slugs = sorted({b.get('slug','') for b in books})
print('slugs:', json.dumps(slugs, ensure_ascii=False))
# find the max id book entry to copy schema
target = None
for b in books:
    if b.get('id') == max_id or b.get('book_id') == max_id:
        target = b
print('sample max-id entry:', json.dumps(target, ensure_ascii=False)[:2000])
