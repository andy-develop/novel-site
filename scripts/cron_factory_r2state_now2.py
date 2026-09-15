import json, os, sys
from dotenv import load_dotenv
load_dotenv('/root/novel-site/.env')
import boto3
from botocore.client import Config

endpoint = os.environ['R2_ENDPOINT']
bucket = os.environ['R2_BUCKET']
s3 = boto3.client('s3', endpoint_url=endpoint,
                  aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
                  aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'],
                  config=Config(signature_version='s3v4'), region_name='auto')

obj = s3.get_object(Bucket=bucket, Key='books.json')
books = json.loads(obj['Body'].read().decode('utf-8'))
ids = [b.get('id') for b in books if isinstance(b.get('id'), int)]
slugs = sorted(b.get('slug', '') for b in books)
max_id = max(ids) if ids else 0
print('count:', len(books))
print('max_id:', max_id)
print('slugs:', ','.join(slugs))
for b in books:
    if b.get('id') == max_id:
        print('SAMPLE:', json.dumps(b, ensure_ascii=False)[:600])
