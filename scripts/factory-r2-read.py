#!/usr/bin/env python3
"""Read R2 novel-data books.json and print max id + slugs. Cron-safe (no execute_code)."""
import json, sys
sys.path.insert(0, '/root/novel-site')
try:
    import boto3
    from botocore.client import Config
    from dotenv import load_dotenv
    load_dotenv('/root/novel-site/.env')
    import os
    s3 = boto3.client('s3', endpoint_url=os.environ['R2_ENDPOINT'],
                      aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
                      aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'],
                      config=Config(signature_version='s3v4'))
    obj = s3.get_object(Bucket=os.environ['R2_BUCKET'], Key='books.json')
    books = json.loads(obj['Body'].read().decode('utf-8'))
    ids = [b.get('id') for b in books if isinstance(b.get('id'), int)]
    print('MAX_ID', max(ids) if ids else 0)
    print('SLUGS', ','.join(str(b.get('slug')) for b in books))
    print('BOOKS', len(books))
except Exception as e:
    print('ERROR', repr(e))
    sys.exit(1)
