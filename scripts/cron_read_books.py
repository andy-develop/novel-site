#!/usr/bin/env python3
"""Read R2 books.json: max id, existing slugs, last few books. Cron-safe (no execute_code)."""
import boto3, os, sys, json
from dotenv import load_dotenv
load_dotenv('/root/novel-site/.env')

client = boto3.client('s3', endpoint_url=os.environ['R2_ENDPOINT'],
    aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'])
obj = client.get_object(Bucket=os.environ['R2_BUCKET'], Key='books.json')
books = json.loads(obj['Body'].read().decode())
ids = sorted(b['id'] for b in books)
slugs = sorted(b['slug'] for b in books)
print('count:', len(books))
print('max_id:', max(ids))
print('all_slugs:', ','.join(slugs))
for b in sorted(books, key=lambda x: x['id'])[-3:]:
    print('last:', b['id'], b['slug'], b['title'], b.get('total_chapters'), b.get('lang'))
