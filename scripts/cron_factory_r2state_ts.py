#!/usr/bin/env python3
"""Read R2 books.json: max id + all slugs (for slug collision check)."""
import boto3, json, os
from dotenv import load_dotenv
load_dotenv('/root/novel-site/.env')

s3 = boto3.client('s3', endpoint_url=os.environ['R2_ENDPOINT'],
                  aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
                  aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'],
                  region_name='auto')
BUCKET = os.environ['R2_BUCKET']
obj = s3.get_object(Bucket=BUCKET, Key='books.json')
books = json.loads(obj['Body'].read().decode('utf-8'))
max_id = max(int(b['id']) for b in books)
slugs = sorted(b.get('slug', '') for b in books)
print(f"MAX_ID={max_id}")
print(f"BOOK_COUNT={len(books)}")
print("SLUGS:", ','.join(slugs))
