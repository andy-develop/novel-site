#!/usr/bin/env python3
"""Read R2 novel-data books.json: print max id, all slugs, lang counts."""
import boto3, json, os
from dotenv import load_dotenv
load_dotenv('/root/novel-site/.env')
s3 = boto3.client('s3', endpoint_url=os.environ['R2_ENDPOINT'],
                  aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
                  aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'],
                  region_name='auto')
obj = s3.get_object(Bucket=os.environ['R2_BUCKET'], Key='books.json')
books = json.loads(obj['Body'].read().decode('utf-8'))
if isinstance(books, dict):
    books = books.get('books', books.get('data', []))
ids = [b.get('id') for b in books if b.get('id') is not None]
print('count:', len(books))
print('max_id:', max(ids))
print('slugs:', sorted(b.get('slug','') for b in books))
langs = {}
for b in books:
    l = b.get('lang','?')
    langs[l] = langs.get(l,0)+1
print('langs:', langs)
# recent english books
eng = [b for b in books if b.get('lang')=='english']
eng.sort(key=lambda b: b.get('id',0))
print('last english ids:', [(b.get('id'), b.get('slug')) for b in eng[-5:]])
