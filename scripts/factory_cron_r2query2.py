#!/usr/bin/env python3
"""Cron factory: query R2 books.json for max id + existing slugs."""
import json, sys
sys.path.insert(0, '/root/novel-site')
try:
    from dotenv import load_dotenv
    load_dotenv('/root/novel-site/.env')
except Exception as e:
    print("dotenv warn:", e)
import os, boto3

endpoint = os.environ.get('R2_ENDPOINT')
key = os.environ.get('R2_ACCESS_KEY_ID')
secret = os.environ.get('R2_SECRET_ACCESS_KEY')
bucket = os.environ.get('R2_BUCKET') or 'novel-data'

s3 = boto3.client('s3', endpoint_url=endpoint, aws_access_key_id=key,
                  aws_secret_access_key=secret, region_name='auto')
obj = s3.get_object(Bucket=bucket, Key='books.json')
data = json.loads(obj['Body'].read().decode('utf-8'))
books = data if isinstance(data, list) else data.get('books', [])
ids = [b.get('id') for b in books if isinstance(b.get('id'), int)]
slugs = [b.get('slug') for b in books if b.get('slug')]
print("MAX_ID:", max(ids) if ids else 0)
print("COUNT:", len(books))
print("SLUGS:", ','.join(sorted(slugs)))
