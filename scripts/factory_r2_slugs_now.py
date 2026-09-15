#!/usr/bin/env python3
"""Dump all R2 books.json slugs to /tmp/r2_slugs.txt and print max id."""
import json, os
import boto3
from dotenv import load_dotenv

load_dotenv('/root/novel-site/.env')
s3 = boto3.client('s3', endpoint_url=os.environ['R2_ENDPOINT'],
                  aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
                  aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'],
                  region_name='auto')
books = json.loads(s3.get_object(Bucket='novel-data', Key='books.json')['Body'].read())
ids = sorted(b['id'] for b in books)
print('max_id:', ids[-1], 'count:', len(books))
slugs = sorted(b.get('slug', '') for b in books)
with open('/tmp/r2_slugs.txt', 'w') as f:
    f.write('\n'.join(slugs))
print('slugs written:', len(slugs))
