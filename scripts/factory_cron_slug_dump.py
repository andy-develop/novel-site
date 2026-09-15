#!/usr/bin/env python3
"""Dump books.json entries for specific slugs."""
import boto3, json, sys

def load_env(path):
    env = {}
    for line in open(path, encoding='utf-8'):
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        env[k] = v.strip().strip('"').strip("'")
    return env

env = load_env("/root/novel-site/.env")
c = boto3.client('s3', endpoint_url=env['R2_ENDPOINT'],
    aws_access_key_id=env['R2_ACCESS_KEY_ID'], aws_secret_access_key=env['R2_SECRET_ACCESS_KEY'])
books = json.loads(c.get_object(Bucket=env['R2_BUCKET'], Key='books.json')['Body'].read())
targets = sys.argv[1:]
for b in books:
    if b.get('slug') in targets:
        print(json.dumps({k: b.get(k) for k in ('id','slug','title','category','intro','total_chapters')}, ensure_ascii=False))
