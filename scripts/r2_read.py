#!/usr/bin/env python3
"""Read R2 books.json: print max id, all slugs, total count."""
import boto3, os, json, sys

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
ids = sorted(b['id'] for b in books)
slugs = sorted(b['slug'] for b in books)
print('COUNT:', len(books))
print('MAX_ID:', max(ids) if ids else 0)
print('ALL_IDS:', ids)
print('SLUGS:', ','.join(slugs))
