#!/usr/bin/env python3
"""Cron recon: parse classics list, read R2 books.json (max id, slugs, sample entry)."""
import re, json, sys
from pathlib import Path

# --- parse classics ---
text = Path('/root/世界名著大全.md').read_text(encoding='utf-8')
titles = re.findall(r'《([^》]+)》', text)
# pair each title with author on same row
pairs = []
for line in text.splitlines():
    m = re.findall(r'《([^》]+)》', line)
    am = re.search(r'\|\s*([^|]+?)\s*\|\s*$', line)
    if m and am:
        pairs.append((m[0], am.group(1).strip()))
print(f"TITLES_FOUND={len(titles)} PAIRS_FOUND={len(pairs)}")

# --- R2 books.json ---
sys.path.insert(0, '/root/novel-site')
import os
from dotenv import load_dotenv
load_dotenv('/root/novel-site/.env')
import boto3
from botocore.client import Config
s3 = boto3.client('s3', endpoint_url=os.environ['R2_ENDPOINT'],
                  aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
                  aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'],
                  config=Config(signature_version='s3v4'), region_name='auto')
bucket = os.environ['R2_BUCKET']
obj = s3.get_object(Bucket=bucket, Key='books.json')
books = json.loads(obj['Body'].read().decode('utf-8'))
print(f"BOOKS_COUNT={len(books)}")
max_id = max(b['id'] for b in books)
print(f"MAX_ID={max_id}")
slugs = [b.get('slug') for b in books if b.get('slug')]
print("SLUGS=" + json.dumps(slugs, ensure_ascii=False))
# sample entry
for b in books:
    if b['id'] == max_id:
        print("LAST_ENTRY=" + json.dumps(b, ensure_ascii=False)[:600])
        break
