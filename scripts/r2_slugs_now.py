#!/usr/bin/env python3
"""Dump all slugs + one full book entry schema. Usage: python3 r2_slugs_now.py [slug-substr]"""
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
slugs = sorted(b.get('slug') for b in books)
print(f"total slugs: {len(slugs)}")
if len(sys.argv) > 1:
    sub = sys.argv[1]
    hits = [s for s in slugs if sub in s]
    print(f"substring '{sub}': {hits}")
# print one full entry for schema
b = sorted(books, key=lambda x: x.get('id',0))[-1]
print("SAMPLE ENTRY:")
print(json.dumps(b, ensure_ascii=False, indent=1)[:1500])
