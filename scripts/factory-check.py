#!/usr/bin/env python3
"""Read R2 books.json: max id, existing slugs, total chapters."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
load_dotenv('/root/novel-site/.env')
import boto3
from botocore.config import Config

s3 = boto3.client(
    's3',
    endpoint_url=os.environ['R2_ENDPOINT'],
    aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'],
    region_name='auto',
    config=Config(signature_version='s3v4'),
)
bucket = os.environ['R2_BUCKET']
obj = s3.get_object(Bucket=bucket, Key='books.json')
books = json.loads(obj['Body'].read().decode('utf-8'))
if isinstance(books, dict):
    books = books.get('books', books.get('data', []))
ids = [b.get('id') for b in books if isinstance(b.get('id'), int)]
slugs = [b.get('slug') for b in books]
print("total books:", len(books))
print("max id:", max(ids) if ids else None)
print("slugs:", ','.join(slugs))
for b in books:
    if b.get('id') == max(ids) if ids else False:
        print("latest book:", json.dumps(b, ensure_ascii=False)[:500])
