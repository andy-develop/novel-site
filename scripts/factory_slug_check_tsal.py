#!/usr/bin/env python3
"""Check slug uniqueness against R2 books.json."""
import boto3, json, os, sys
from dotenv import load_dotenv
load_dotenv('/root/novel-site/.env')
s3 = boto3.client('s3', endpoint_url=os.environ['R2_ENDPOINT'],
                  aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
                  aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'], region_name='auto')
books = json.loads(s3.get_object(Bucket=os.environ['R2_BUCKET'], Key='books.json')['Body'].read())
slugs = set(b.get('slug') for b in books)
cand = sys.argv[1]
print('candidate:', cand, '| exists:', cand in slugs)
# also confirm max id
print('max_id:', max(b['id'] for b in books))
