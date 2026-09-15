#!/usr/bin/env python3
"""Fetch R2 books.json, print max id + existing slugs + count. Run from /root/novel-site."""
import boto3, json, os, sys
from dotenv import load_dotenv
load_dotenv('/root/novel-site/.env')
s3 = boto3.client('s3',
    endpoint_url=os.environ['R2_ENDPOINT'],
    aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'],
    region_name='auto')
obj = s3.get_object(Bucket=os.environ['R2_BUCKET'], Key='books.json')
books = json.loads(obj['Body'].read())
ids = sorted(b['id'] for b in books)
slugs = sorted(b.get('slug', '') for b in books)
print("COUNT", len(books))
print("MAX_ID", max(ids))
print("IDS_SAMPLE", ids[-15:])
print("SLUGS")
for s in slugs:
    print(s)
