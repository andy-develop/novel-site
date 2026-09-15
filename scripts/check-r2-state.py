#!/usr/bin/env python3
"""Check R2 novel-data state: max book id, existing slugs, book count."""
import json, sys
sys.path.insert(0, '/root/novel-site')
import boto3
from dotenv import load_dotenv
load_dotenv('/root/novel-site/.env')
import os

s3 = boto3.client(
    's3',
    endpoint_url=os.environ['R2_ENDPOINT'],
    aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'],
    region_name='auto',
)
bucket = os.environ['R2_BUCKET']
obj = s3.get_object(Bucket=bucket, Key='books.json')
books = json.loads(obj['Body'].read().decode('utf-8'))
print('total books:', len(books))
ids = [b.get('id') for b in books]
max_id = max([i for i in ids if isinstance(i, int)])
print('max id:', max_id)
slugs = sorted([b.get('slug','') for b in books])
print('slugs:', ','.join(slugs))
# also list any catalog_ files to double check ids
resp = s3.list_objects_v2(Bucket=bucket, Prefix='catalog_')
cats = [k['Key'] for k in resp.get('Contents', [])]
print('catalog files:', ','.join(cats))
