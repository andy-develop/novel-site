#!/usr/bin/env python3
"""Independent R2 read-back for book 1406."""
import json, sys, os
sys.path.insert(0, '/root/novel-site/scripts')
import boto3
from dotenv import load_dotenv
load_dotenv('/root/novel-site/.env')

c = boto3.client('s3', endpoint_url=os.environ['R2_ENDPOINT'],
    aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'])

books = json.loads(c.get_object(Bucket=os.environ['R2_BUCKET'], Key='books.json')['Body'].read())
entry = [b for b in books if int(b['id']) == 1406][0]
print("BOOKS ENTRY:", json.dumps({k: entry.get(k) for k in ['id','slug','title','author','category','total_chapters','lang','tags']}, ensure_ascii=False))

cat = json.loads(c.get_object(Bucket=os.environ['R2_BUCKET'], Key='catalog_1406.json')['Body'].read())
print("CATALOG chapters:", len(cat['chapters']))
keys_ok = all('chapter_id' in ch for ch in cat['chapters'])
print("catalog uses chapter_id:", keys_ok)
print("catalog first:", cat['chapters'][0], "last:", cat['chapters'][-1])

bad = 0
for n in [1, 14, 28]:
    ch = json.loads(c.get_object(Bucket=os.environ['R2_BUCKET'], Key=f'1406/{n}.json')['Body'].read())
    ok = (ch['book_id'] == 1406 and ch['chapter_id'] == n and len(ch['content']) > 20 and len(ch.get('highlight','')) > 10)
    print(f"ch{n}: id={ch['chapter_id']} paras={len(ch['content'])} title={ch['title'][:50]!r} hl_len={len(ch.get('highlight',''))} OK={ok}")
    if not ok: bad += 1
print("RESULT:", "PASS" if bad == 0 and len(cat['chapters']) == 28 else "FAIL")
