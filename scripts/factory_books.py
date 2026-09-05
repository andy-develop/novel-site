#!/usr/bin/env python3
"""Read R2 books.json: max id + existing slugs."""
import boto3, os, json
from dotenv import load_dotenv
load_dotenv('/root/novel-site/.env')
s3 = boto3.client('s3', endpoint_url=os.environ['R2_ENDPOINT'],
                  aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
                  aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'],
                  region_name='auto')
r = s3.get_object(Bucket=os.environ['R2_BUCKET'], Key='books.json')
books = json.loads(r['Body'].read())
ids = sorted(b['id'] for b in books)
print('num books:', len(books))
print('max id:', max(ids))
print('ids:', ids[-12:])
slugs = sorted(b['slug'] for b in books)
print('slugs:', slugs)
