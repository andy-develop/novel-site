#!/usr/bin/env python3
"""Cron helper: print max book id + existing slugs + total from R2 books.json."""
import os, json, sys
import boto3

def load_env(path):
    env = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env

env = load_env('/root/novel-site/.env')
client = boto3.client('s3', endpoint_url=env['R2_ENDPOINT'],
                      aws_access_key_id=env['R2_ACCESS_KEY_ID'],
                      aws_secret_access_key=env['R2_SECRET_ACCESS_KEY'])
obj = client.get_object(Bucket=env['R2_BUCKET'], Key='books.json')
books = json.loads(obj['Body'].read().decode('utf-8'))
ids = [b.get('id') for b in books if isinstance(b.get('id'), int)]
slugs = [b.get('slug') for b in books if b.get('slug')]
print('MAX_ID', max(ids) if ids else 0)
print('TOTAL', len(books))
print('SLUGS', ','.join(slugs))
