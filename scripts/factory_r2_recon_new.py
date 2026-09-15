#!/usr/bin/env python3
"""Read R2 books.json: max id, existing slugs, count (batch factory recon)."""
import json, os, sys
os.chdir('/root/novel-site')
from dotenv import load_dotenv
load_dotenv('/root/novel-site/.env')
import boto3
from botocore.config import Config

endpoint = os.environ['R2_ENDPOINT']
bucket = os.environ['R2_BUCKET']
s3 = boto3.client('s3', endpoint_url=endpoint,
                  aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
                  aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'],
                  config=Config(signature_version='s3v4'), region_name='auto')
try:
    obj = s3.get_object(Bucket=bucket, Key='books.json')
    books = json.loads(obj['Body'].read().decode('utf-8'))
except Exception as e:
    print("ERROR", e); sys.exit(1)

books = books if isinstance(books, list) else books.get('books', [])
ids = sorted(b['id'] for b in books if isinstance(b.get('id'), int))
print("count:", len(books))
print("max_id:", max(ids) if ids else 0)
print("slugs:", json.dumps(sorted(b.get('slug','') for b in books)))
