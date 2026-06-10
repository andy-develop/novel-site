#!/usr/bin/env python3
"""R2 上传脚本 — 从文件读凭据"""
import json, os, sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import boto3

AK_FILE = '/tmp/r2_key.txt'
SK_FILE = '/tmp/r2_secret.txt'

with open(AK_FILE) as f:
    ACCESS_KEY = f.read().strip()
with open(SK_FILE) as f:
    SECRET_KEY = f.read().strip()

BUCKET = 'novel-data'
ENDPOINT = 'https://38481ae73b0bdbfbc9b619dc18526041.r2.cloudflarestorage.com'
DATA_DIR = Path('/root/novel-site/data')

print(f'Key length: {len(ACCESS_KEY)}')
print(f'Secret length: {len(SECRET_KEY)}')

client = boto3.client(
    's3', endpoint_url=ENDPOINT,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
)

def upload_file(filepath):
    key = str(filepath.relative_to(DATA_DIR))
    try:
        with open(filepath, 'rb') as f:
            client.put_object(
                Bucket=BUCKET, Key=key, Body=f,
                ContentType='application/json',
                CacheControl='public, max-age=31536000, immutable',
            )
        return True, key
    except Exception as e:
        return False, f'{key}: {e}'

def main():
    files = [f for f in DATA_DIR.rglob('*.json') if f.name != 'books.json']
    print(f'Uploading {len(files)} files to {BUCKET}...')
    ok, fail = 0, 0
    with ThreadPoolExecutor(max_workers=20) as pool:
        fut = {pool.submit(upload_file, f): f for f in files}
        for f in as_completed(fut):
            s, m = f.result()
            if s:
                ok += 1
            else:
                fail += 1
                if fail <= 5:
                    print(f'  FAIL: {m}')
    print(f'Done: {ok} ok, {fail} failed')

if __name__ == '__main__':
    main()
