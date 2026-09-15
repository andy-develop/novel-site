#!/usr/bin/env python3
"""Read R2 books.json: print max id, count, and all slugs."""
import os, json, boto3
from dotenv import load_dotenv
load_dotenv('/root/novel-site/.env')
client = boto3.client('s3', endpoint_url=os.environ['R2_ENDPOINT'],
    aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'])
obj = client.get_object(Bucket=os.environ['R2_BUCKET'], Key='books.json')
books = json.loads(obj['Body'].read())
ids = [b.get('id') for b in books if isinstance(b.get('id'), int)]
print(f"COUNT={len(books)} MAX_ID={max(ids) if ids else 0}")
slugs = sorted(b.get('slug','') for b in books)
print("SLUGS=" + ",".join(slugs))
