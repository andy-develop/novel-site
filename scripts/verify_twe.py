#!/usr/bin/env python3
"""Final R2 read-back of book 1462."""
import json, os, sys
sys.path.insert(0, '/root/novel-site')
from dotenv import load_dotenv
load_dotenv('/root/novel-site/.env')
import boto3
from botocore.client import Config
s3 = boto3.client('s3', endpoint_url=os.environ['R2_ENDPOINT'], aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'], aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'], config=Config(signature_version='s3v4'), region_name='auto')
books = json.loads(s3.get_object(Bucket='novel-data', Key='books.json')['Body'].read())
e = [b for b in books if b.get('id') == 1462][0]
print('entry:', json.dumps({k: e.get(k) for k in ['id','slug','title','author','category','total_chapters','lang','tags']}, ensure_ascii=False))
cat = json.loads(s3.get_object(Bucket='novel-data', Key='catalog_1462.json')['Body'].read())
print('catalog chapters:', len(cat['chapters']), '| first:', cat['chapters'][0], '| last:', cat['chapters'][-1])
ch1 = json.loads(s3.get_object(Bucket='novel-data', Key='1462/1.json')['Body'].read())
ch28 = json.loads(s3.get_object(Bucket='novel-data', Key='1462/28.json')['Body'].read())
print('ch1:', ch1['chapter_id'], ch1['title'], '| hl:', ch1['highlight'][:60], '| paras:', len(ch1['content']))
print('ch28:', ch28['chapter_id'], ch28['title'], '| hl:', ch28['highlight'][:60], '| paras:', len(ch28['content']))
