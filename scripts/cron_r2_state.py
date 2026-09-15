#!/usr/bin/env python3
"""Cron helper: read R2 books.json state (max id, existing slugs, langs)."""
import json, sys
import boto3
from dotenv import load_dotenv

load_dotenv('/root/novel-site/.env')

s3 = boto3.client(
    's3',
    endpoint_url='https://38481ae73b0bdbfbc9b619dc18526041.r2.cloudflarestorage.com',
    aws_access_key_id=open('/root/novel-site/.env').read().split('R2_ACCESS_KEY_ID=')[1].split('\n')[0].strip('"'),
    aws_secret_access_key=open('/root/novel-site/.env').read().split('R2_SECRET_ACCESS_KEY=')[1].split('\n')[0].strip('"'),
    region_name='auto',
)
obj = s3.get_object(Bucket='novel-data', Key='books.json')
books = json.loads(obj['Body'].read().decode())
print('TOTAL', len(books))
ids = sorted(b['id'] for b in books)
print('MAX_ID', ids[-1])
print('SLUGS', ','.join(b.get('slug', '') for b in books))
print('LANGS', {l: sum(1 for b in books if b.get('lang') == l) for l in set(b.get('lang', '?') for b in books)})
