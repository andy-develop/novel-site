#!/usr/bin/env python3
import json, boto3
from botocore.config import Config
env = {}
for line in open('/root/novel-site/.env'):
    line = line.strip()
    if not line or line.startswith('#') or '=' not in line:
        continue
    k, v = line.split('=', 1)
    env[k.strip()] = v.strip().strip('"').strip("'")
s3 = boto3.client('s3', endpoint_url=env['R2_ENDPOINT'],
                  aws_access_key_id=env['R2_ACCESS_KEY_ID'],
                  aws_secret_access_key=env['R2_SECRET_ACCESS_KEY'],
                  config=Config(signature_version='s3v4'), region_name='auto')
books = json.loads(s3.get_object(Bucket='novel-data', Key='books.json')['Body'].read().decode())
if isinstance(books, dict):
    books = books.get('books', books.get('data', []))
json.dump(books, open('/root/novels/_factory_books.json', 'w'), ensure_ascii=False)
print("books:", len(books))
kw = ['kafka', 'the trial', 'bureaucra', 'process', 'four generation', 'hutong', 'occupation', 'condemn', 'notice', 'compliance', 'evict', 'tribunal']
slugs = {b.get('slug') for b in books}
for t in ['notice-of-condemnation', 'the-notice', 'case-number', 'under-one-roof']:
    print('slug taken?', t, t in slugs)
for k in kw:
    hits = [b.get('slug') for b in books if k in ((b.get('title') or '') + ' ' + (b.get('intro') or '') + ' ' + ' '.join(b.get('tags') or [])).lower()]
    print(f'[{k}] {len(hits)}', hits[:6])
