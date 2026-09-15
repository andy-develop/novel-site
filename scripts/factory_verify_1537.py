#!/usr/bin/env python3
"""Verify books.json entry for id 1537."""
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
b = next((x for x in books if x.get('id') == 1537), None)
print(json.dumps(b, ensure_ascii=False, indent=1))
# catalog check
c = json.loads(s3.get_object(Bucket=env['R2_BUCKET'], Key='catalog_1537.json')['Body'].read().decode())
ch = c.get('chapters', c if isinstance(c, list) else [])
print('catalog chapters:', len(ch))
print('first entry keys:', list(ch[0].keys()) if ch else None)
# spot check chapter 1 object
ch1 = json.loads(s3.get_object(Bucket=env['R2_BUCKET'], Key='1537/1.json')['Body'].read().decode())
print('ch1 keys:', list(ch1.keys()))
print('ch1 title:', ch1.get('title'))
print('ch1 has highlight:', bool(ch1.get('highlight')), '| len content:', len(ch1.get('content', [])))
