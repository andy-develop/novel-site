#!/usr/bin/env python3
"""Read R2 books.json: max id, count, slugs, last few books. Usage: python3 r2_state_now.py"""
import json, sys
sys.path.insert(0, '/root/novel-site')
try:
    from dotenv import load_dotenv
    load_dotenv('/root/novel-site/.env')
except Exception as e:
    print("dotenv fail", e)
import os, boto3

endpoint = os.environ['R2_ENDPOINT']
bucket = os.environ['R2_BUCKET']
s3 = boto3.client('s3', endpoint_url=endpoint,
                  aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
                  aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'],
                  region_name='auto')
obj = s3.get_object(Bucket=bucket, Key='books.json')
books = json.loads(obj['Body'].read().decode('utf-8'))
ids = [b.get('id') for b in books]
maxid = max(ids)
slugs = [b.get('slug') for b in books]
print(f"count={len(books)} max_id={maxid} next_id={maxid+1}")
print("recent:", [(b.get('id'), b.get('slug'), b.get('title'), b.get('total_chapters'), b.get('lang')) for b in sorted(books, key=lambda x: x.get('id',0))[-8:]])
