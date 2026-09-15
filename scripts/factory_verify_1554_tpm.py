#!/usr/bin/env python3
"""Verify R2 state for a book id: books.json entry, catalog count, chapter highlights."""
import boto3, json, os, sys
from dotenv import load_dotenv
load_dotenv('/root/novel-site/.env')

book_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1554
s3 = boto3.client('s3', endpoint_url=os.environ['R2_ENDPOINT'],
                  aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
                  aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'],
                  region_name='auto')
BUCKET = os.environ['R2_BUCKET']

books = json.loads(s3.get_object(Bucket=BUCKET, Key='books.json')['Body'].read())
entry = next((b for b in books if int(b.get('id', -1)) == book_id), None)
print("BOOKS_ENTRY:", json.dumps(entry, ensure_ascii=False)[:300] if entry else "NOT FOUND")

cat = json.loads(s3.get_object(Bucket=BUCKET, Key=f'catalog_{book_id}.json')['Body'].read())
chs = cat.get('chapters', cat if isinstance(cat, list) else [])
print("CATALOG_CHAPTERS:", len(chs), "first:", chs[0].get('chapter_id'), chs[0].get('title', '')[:40])

# chapter objects + highlights
no_hl = []
for i in range(1, 28):
    obj = json.loads(s3.get_object(Bucket=BUCKET, Key=f'{book_id}/{i}.json')['Body'].read())
    if not obj.get('highlight'):
        no_hl.append(i)
print("CHAPTERS_1_27_OK, MISSING_HIGHLIGHTS:", no_hl if no_hl else "none")
# check chapter 27 content head
print("CH27_TITLE:", obj.get('title'), "| words:", len(obj.get('content', '').split()))
