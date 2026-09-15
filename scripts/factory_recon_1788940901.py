#!/usr/bin/env python3
"""Recon R2 books.json: max id, all slugs, check candidate slug."""
import json, sys, boto3
from dotenv import load_dotenv
load_dotenv('/root/novel-site/.env')
import os

s3 = boto3.client('s3', endpoint_url=os.environ['R2_ENDPOINT'],
                  aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
                  aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'],
                  region_name='auto')
bucket = os.environ['R2_BUCKET']
obj = s3.get_object(Bucket=bucket, Key='books.json')
books = json.loads(obj['Body'].read().decode('utf-8'))
items = books if isinstance(books, list) else books.get('books', books.get('data', []))
ids = [b.get('id') for b in items if isinstance(b, dict) and b.get('id') is not None]
maxid = max(ids) if ids else 0
print(f"BOOKS_COUNT: {len(items)}  MAX_ID: {maxid}")
slugs = [b.get('slug') for b in items if isinstance(b, dict) and b.get('slug')]
print("SLUGS:")
for s in sorted(slugs):
    print(" ", s)
cand = sys.argv[1] if len(sys.argv) > 1 else 'better-to-reign'
print(f"CANDIDATE_SLUG '{cand}' EXISTS: {cand in slugs}")
