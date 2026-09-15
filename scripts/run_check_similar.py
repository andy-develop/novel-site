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
want = {'cordelia-buys-the-empire-back', 'the-camellia-game', 'the-camellia-code', 'camellia-unchained', 'the-red-camellia', 'marguerite-acquires-the-camellias'}
for b in books:
    if b.get('slug') in want:
        print(b.get('id'), '|', b.get('slug'), '|', b.get('title'), '|', str(b.get('intro') or b.get('premise'))[:200])
        print('   tags:', b.get('tags'), 'cat:', b.get('category'))
print('--- also check lear/king-lear slugs')
for b in books:
    s = b.get('slug') or ''
    if 'lear' in s or 'king-lear' in s:
        print(b.get('id'), s, b.get('title'))
