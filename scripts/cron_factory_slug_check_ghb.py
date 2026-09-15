#!/usr/bin/env python3
"""Check slug availability in R2 books.json."""
import boto3, json, os
from dotenv import load_dotenv
load_dotenv('/root/novel-site/.env')
s3 = boto3.client('s3', endpoint_url=os.environ['R2_ENDPOINT'], aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'], aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'], region_name='auto')
r = s3.get_object(Bucket='novel-data', Key='books.json')
books = json.loads(r['Body'].read())
cands = ['the-girl-he-built', 'his-creature', 'built-girl', 'made-girl', 'not-his-creature', 'created-girl', 'the-second-face']
existing = {b['slug'] for b in books}
for c in cands:
    print(c, 'TAKEN' if c in existing else 'free')
