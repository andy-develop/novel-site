#!/usr/bin/env python3
"""Look up book(s) by slug substring. Usage: python3 r2_lookup_now.py <substr>"""
import json, sys
sys.path.insert(0, '/root/novel-site')
try:
    from dotenv import load_dotenv
    load_dotenv('/root/novel-site/.env')
except Exception as e:
    print("dotenv fail", e)
import os, boto3

s3 = boto3.client('s3', endpoint_url=os.environ['R2_ENDPOINT'],
                  aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
                  aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'],
                  region_name='auto')
books = json.loads(s3.get_object(Bucket=os.environ['R2_BUCKET'], Key='books.json')['Body'].read().decode('utf-8'))
sub = sys.argv[1]
for b in books:
    blob = json.dumps(b, ensure_ascii=False)
    if sub in (b.get('slug') or '') or sub in (b.get('title') or ''):
        print(json.dumps(b, ensure_ascii=False, indent=1))
        print('---')
