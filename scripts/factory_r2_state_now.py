#!/usr/bin/env python3
"""Read R2 books.json: print max id, count, and all slugs+titles."""
import json, sys, os
sys.path.insert(0, '/root/novel-site')
try:
    from dotenv import load_dotenv
    load_dotenv('/root/novel-site/.env')
except Exception:
    pass
import boto3
from botocore.config import Config

key = os.environ['R2_ACCESS_KEY_ID']
secret = os.environ['R2_SECRET_ACCESS_KEY']
endpoint = os.environ['R2_ENDPOINT']
bucket = os.environ['R2_BUCKET']

s3 = boto3.client('s3', endpoint_url=endpoint, aws_access_key_id=key,
                  aws_secret_access_key=secret, config=Config(signature_version='s3v4'), region_name='auto')
obj = s3.get_object(Bucket=bucket, Key='books.json')
books = json.loads(obj['Body'].read().decode('utf-8'))
ids = [b.get('id') for b in books if isinstance(b.get('id'), int)]
print('max_id:', max(ids))
print('count:', len(books))
for b in sorted(books, key=lambda x: x.get('id', 0)):
    print(b.get('id'), '|', b.get('slug'), '|', b.get('title'), '|', b.get('lang', ''), '|', b.get('total_chapters'))
