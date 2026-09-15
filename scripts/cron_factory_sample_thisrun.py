#!/usr/bin/env python3
"""Print 3 sample English book entries from R2 books.json (format reference)."""
import json, os
import boto3
from dotenv import load_dotenv

load_dotenv('/root/novel-site/.env')
client = boto3.client('s3',
    endpoint_url=os.environ['R2_ENDPOINT'],
    aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'])
obj = client.get_object(Bucket='novel-data', Key='books.json')
books = json.loads(obj['Body'].read())
en = [b for b in books if b.get('lang') in ('english', 'en')]
for b in en[-5:]:
    print(json.dumps(b, ensure_ascii=False)[:500])
