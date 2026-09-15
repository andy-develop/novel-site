#!/usr/bin/env python3
"""Cron factory: read R2 books.json, report max id + slug collision check."""
import boto3, json, os
from dotenv import load_dotenv
load_dotenv('/root/novel-site/.env')
s3 = boto3.client('s3', endpoint_url=os.environ['R2_ENDPOINT'],
                  aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
                  aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'])
books = json.loads(s3.get_object(Bucket=os.environ['R2_BUCKET'], Key='books.json')['Body'].read())
ids = [b.get('id') for b in books if isinstance(b.get('id'), int)]
slugs = {b.get('slug'): b.get('id') for b in books if b.get('slug')}
print('total_books:', len(books))
print('max_id:', max(ids))
print('slug the-shining-prince exists:', 'the-shining-prince' in slugs)
for k, v in slugs.items():
    if 'shining' in k or 'prince' in k or 'genji' in k or 'history' in k or 'morante' in k:
        print('COLLISION-CANDIDATE:', k, '->', v)
