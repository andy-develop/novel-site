#!/usr/bin/env python3
"""Read books.json from R2 and print max id + all slugs (for slug collision check)."""
import json, sys
import boto3
from botocore.config import Config

sys.path.insert(0, '/root/novel-site')
from dotenv import load_dotenv
load_dotenv('/root/novel-site/.env')
import os

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
ids = [b.get('id') for b in books]
ids_sorted = sorted([i for i in ids if isinstance(i, int)])
print("TOTAL:", len(books))
print("MAX_ID:", max(ids_sorted) if ids_sorted else 0)
print("IDS:", ids_sorted[-15:])
print("SLUGS:")
for b in books:
    print(" ", b.get('id'), b.get('slug'), '|', str(b.get('title'))[:40], '|', b.get('lang'))
