#!/usr/bin/env python3
"""Check slug uniqueness for the-red-camellia + print max id."""
import json, os, sys
from dotenv import load_dotenv
load_dotenv('/root/novel-site/.env')
import boto3
c = boto3.client('s3', endpoint_url=os.environ['R2_ENDPOINT'],
    aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'])
books = json.loads(c.get_object(Bucket='novel-data', Key='books.json')['Body'].read())
ids = [b.get('id') for b in books if isinstance(b.get('id'), int)]
slugs = [b.get('slug','') for b in books]
target = 'the-red-camellia'
print("max id:", max(ids))
print("slug free:", target not in slugs)
print("count with slug prefix 'the-red':", [s for s in slugs if s.startswith('the-red')])
