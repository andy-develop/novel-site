#!/usr/bin/env python3
"""Dump all existing slugs from R2 books.json."""
import json, boto3
from botocore.config import Config

env = {}
with open('/root/novel-site/.env') as f:
    for line in f:
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            env[k] = v.strip().strip('"').strip("'")

s3 = boto3.client('s3', endpoint_url=env['R2_ENDPOINT'], aws_access_key_id=env['R2_ACCESS_KEY_ID'],
                  aws_secret_access_key=env['R2_SECRET_ACCESS_KEY'], config=Config(signature_version='s3v4'),
                  region_name='auto')
obj = s3.get_object(Bucket=env['R2_BUCKET'], Key='books.json')
books = json.loads(obj['Body'].read().decode())
slugs = sorted(b.get('slug') for b in books if b.get('slug'))
print('total slugs:', len(slugs))
for s in slugs:
    print(s)
