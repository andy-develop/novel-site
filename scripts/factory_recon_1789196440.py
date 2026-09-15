#!/usr/bin/env python3
"""Recon: read R2 books.json -> max id + all slugs (for collision check)."""
import json, os, sys
import boto3
from botocore.client import Config
from dotenv import load_dotenv

load_dotenv('/root/novel-site/.env')

s3 = boto3.client('s3',
    endpoint_url=os.environ['R2_ENDPOINT'],
    aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'],
    config=Config(signature_version='s3v4'),
    region_name='auto')

BUCKET = os.environ.get('R2_BUCKET', 'novel-data')

try:
    obj = s3.get_object(Bucket=BUCKET, Key='books.json')
    books = json.loads(obj['Body'].read().decode('utf-8'))
except Exception as e:
    print('ERROR reading books.json:', e)
    sys.exit(1)

ids = [b.get('id') for b in books if isinstance(b.get('id'), int)]
ids += [b.get('id') for b in books if isinstance(b.get('id'), str) and b.get('id').isdigit()]
print('total books:', len(books))
print('max id:', max(ids) if ids else 0)
print('next id:', (max(ids) + 1) if ids else 1)
slugs = sorted(b.get('slug', '') for b in books)
print('all slugs:', ', '.join(slugs))
