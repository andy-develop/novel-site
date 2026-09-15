#!/usr/bin/env python3
"""Fetch books.json from R2 and print max id + all slugs."""
import json, os
os.chdir('/root/novel-site')
from dotenv import load_dotenv
load_dotenv('/root/novel-site/.env')
import boto3
from botocore.client import Config

s3 = boto3.client(
    's3',
    endpoint_url=os.environ['R2_ENDPOINT'],
    aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'],
    config=Config(signature_version='s3v4'),
    region_name='auto',
)
obj = s3.get_object(Bucket=os.environ['R2_BUCKET'], Key='books.json')
books = json.loads(obj['Body'].read().decode('utf-8'))
ids = [b.get('id') for b in books if isinstance(b.get('id'), int)]
print('MAX_ID', max(ids) if ids else 0)
print('N_BOOKS', len(books))
slugs = sorted(b.get('slug', '') for b in books)
print('SLUGS', ','.join(slugs))
# print first book entry shape
if books:
    print('SAMPLE_KEYS', sorted(books[0].keys()))
    b0 = dict(books[0])
    b0.pop('description', None)
    b0.pop('intro', None)
    print('SAMPLE', json.dumps(b0)[:500])
