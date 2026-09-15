#!/usr/bin/env python3
"""Read R2 books.json: max id, existing slugs, count. Run from /root/novel-site."""
import json, sys
from dotenv import load_dotenv
load_dotenv('/root/novel-site/.env')
import boto3, os

endpoint = os.environ['R2_ENDPOINT']
bucket = os.environ['R2_BUCKET']
s3 = boto3.client('s3', endpoint_url=endpoint,
                  aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
                  aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'],
                  region_name='auto')
obj = s3.get_object(Bucket=bucket, Key='books.json')
data = json.loads(obj['Body'].read().decode('utf-8'))
books = data if isinstance(data, list) else data.get('books', data)
ids = sorted(int(b['id']) for b in books)
print('count:', len(books))
print('max_id:', max(ids))
print('last5_ids:', ids[-5:])
slugs = sorted(b.get('slug','') for b in books)
print('slugs:')
for s in slugs:
    print(' ', s)
