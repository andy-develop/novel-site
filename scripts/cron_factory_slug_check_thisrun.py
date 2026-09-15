#!/usr/bin/env python3
"""Read R2 books.json: print max id, total books, all slugs (collision check)."""
import json, os, sys
import boto3
from dotenv import load_dotenv

load_dotenv('/root/novel-site/.env')
client = boto3.client('s3',
    endpoint_url=os.environ['R2_ENDPOINT'],
    aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'])
obj = client.get_object(Bucket='novel-data', Key='books.json')
books = json.loads(obj['Body'].read())
ids = sorted(b['id'] for b in books)
print(f"TOTAL_BOOKS={len(books)}")
print(f"MAX_ID={ids[-1]}")
print(f"NEW_ID={ids[-1]+1}")
slugs = sorted(b['slug'] for b in books)
print("SLUGS=" + ",".join(slugs))
