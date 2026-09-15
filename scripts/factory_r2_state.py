#!/usr/bin/env python3
"""Read R2 books.json: max id, count, existing slugs, last entries."""
import json, sys
sys.path.insert(0, '/root/novel-site/scripts')
try:
    from r2_books import get_books  # may exist
except Exception:
    get_books = None

from dotenv import load_dotenv
load_dotenv('/root/novel-site/.env')
import os, boto3

client = boto3.client('s3',
    endpoint_url=os.environ['R2_ENDPOINT'],
    aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'])
resp = client.get_object(Bucket='novel-data', Key='books.json')
books = json.loads(resp['Body'].read().decode('utf-8'))
print("total books:", len(books))
ids = [b.get('id') for b in books if isinstance(b.get('id'), int)]
print("max id:", max(ids) if ids else None)
print("slugs:", sorted(b.get('slug','') for b in books)[-12:])
print("--- last 5 by id ---")
for b in sorted(books, key=lambda x: x.get('id',0))[-5:]:
    print(b.get('id'), b.get('slug'), '|', b.get('title'), '|', b.get('lang'), '| ch:', b.get('total_chapters'))
