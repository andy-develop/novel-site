#!/usr/bin/env python3
"""Check slug uniqueness and max book id in R2 books.json."""
import json, boto3, sys

env = {}
for line in open('/root/novel-site/.env'):
    line = line.strip()
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        env[k] = v.strip().strip('"').strip("'")

c = boto3.client('s3', endpoint_url=env['R2_ENDPOINT'],
                 aws_access_key_id=env['R2_ACCESS_KEY_ID'],
                 aws_secret_access_key=env['R2_SECRET_ACCESS_KEY'])
books = json.loads(c.get_object(Bucket=env['R2_BUCKET'], Key='books.json')['Body'].read())
target = sys.argv[1] if len(sys.argv) > 1 else 'vanity-pilgrim'
hits = [b for b in books if b.get('slug') == target]
print('slug hits for %s:' % target, hits if hits else 'NONE - unique')
print('max id:', max(b.get('id', 0) for b in books))
print('total books:', len(books))
