#!/usr/bin/env python3
"""Verify books.json entry for book id."""
import os, json
from dotenv import load_dotenv
load_dotenv('/root/novel-site/.env')
import boto3

s3 = boto3.client('s3', endpoint_url=os.environ['R2_ENDPOINT'],
                  aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
                  aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'],
                  region_name='auto')
books = json.loads(s3.get_object(Bucket=os.environ['R2_BUCKET'], Key='books.json')['Body'].read())
entry = [b for b in books if b.get('id') == 1388]
print(json.dumps(entry, ensure_ascii=False, indent=1))
cat = json.loads(s3.get_object(Bucket=os.environ['R2_BUCKET'], Key='catalog_1388.json')['Body'].read())
print("catalog chapters:", len(cat['chapters']), "first:", cat['chapters'][0], "last:", cat['chapters'][-1])
