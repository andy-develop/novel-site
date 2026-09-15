#!/usr/bin/env python3
"""Check candidate slugs against R2 books.json."""
import os, json, sys, boto3
from dotenv import load_dotenv
load_dotenv('/root/novel-site/.env')
client = boto3.client('s3', endpoint_url=os.environ['R2_ENDPOINT'],
    aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'])
books = json.loads(client.get_object(Bucket=os.environ['R2_BUCKET'], Key='books.json')['Body'].read())
cands = sys.argv[1:] or ['she-plays-the-fair']
slugs = {b.get('slug') for b in books}
ids = [b.get('id') for b in books if isinstance(b.get('id'), int)]
for c in cands:
    print(f"{c}: {'TAKEN' if c in slugs else 'FREE'}")
print("MAX_ID", max(ids))
