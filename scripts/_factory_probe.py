#!/usr/bin/env python3
"""Probe R2 books.json: max id, existing slugs, sample classics with timestamp seed."""
import os, re, json, random, sys
from dotenv import load_dotenv
import boto3

load_dotenv('/root/novel-site/.env')

s3 = boto3.client(
    's3',
    endpoint_url=os.environ['R2_ENDPOINT'],
    aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'],
    region_name='auto',
)
try:
    obj = s3.get_object(Bucket=os.environ['R2_BUCKET'], Key='books.json')
    books = json.loads(obj['Body'].read().decode('utf-8'))
    items = books if isinstance(books, list) else books.get('books', books.get('data', []))
    print('BOOKS_TYPE', type(books).__name__, 'N', len(items))
    maxid = 0
    slugs = set()
    for b in items:
        bid = b.get('id')
        if isinstance(bid, int):
            maxid = max(maxid, bid)
        if b.get('slug'):
            slugs.add(b['slug'])
    print('MAX_ID', maxid)
    print('SLUGS', sorted(slugs))
except Exception as e:
    print('R2_ERR', repr(e))

# Parse classics
text = open('/root/世界名著大全.md', encoding='utf-8').read()
titles = re.findall(r'《([^》]+)》', text)
print('CLASSICS_N', len(titles))

seed = int(sys.argv[1]) if len(sys.argv) > 1 else int(time.time())
random.seed(seed)
pairs = []
for _ in range(6):
    c = random.sample(titles, 2)
    pairs.append(c)
print('SEED', seed)
for i, p in enumerate(pairs):
    print(f'PAIR{i}: {p[0]} | {p[1]}')
