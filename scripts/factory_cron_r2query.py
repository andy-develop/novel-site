#!/usr/bin/env python3
"""Query R2 novel-data books.json: max id, existing slugs, book count."""
import json, sys
sys.path.insert(0, '/root/novel-site/scripts')
try:
    import boto3
except ImportError:
    boto3 = None
from dotenv import load_dotenv
load_dotenv('/root/novel-site/.env')
import os

if boto3 is None:
    print("NO_BOTO3")
    sys.exit(1)

s3 = boto3.client(
    's3',
    endpoint_url=os.environ['R2_ENDPOINT'],
    aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'],
    region_name='auto',
)
obj = s3.get_object(Bucket=os.environ['R2_BUCKET'], Key='books.json')
books = json.loads(obj['Body'].read())
print("BOOK_COUNT", len(books))
ids = sorted(int(b['id']) for b in books)
print("MAX_ID", max(ids))
print("MIN_ID", min(ids))
slugs = sorted(b.get('slug','?') for b in books)
print("SLUGS", ','.join(slugs))
print("ENGLISH_BOOKS", sum(1 for b in books if b.get('lang')=='english'))
# print titles of last 5 books for context
for b in sorted(books, key=lambda x: int(x['id']))[-6:]:
    print("LAST", b.get('id'), b.get('slug'), b.get('title'), b.get('total_chapters'), b.get('lang'))
