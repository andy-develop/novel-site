#!/usr/bin/env python3
"""Regenerate the missing highlight for ch21 and re-PUT the R2 object."""
import sys, os, json, importlib.util
spec = importlib.util.spec_from_file_location('um', '/root/novel-site/scripts/upload-manual.py')
um = importlib.util.module_from_spec(spec)
spec.loader.exec_module(um)
load_env, llm_highlight, parse_chapter = um.load_env, um.llm_highlight, um.parse_chapter

env = load_env('/root/novel-site/.env')
import boto3
c = boto3.client('s3', endpoint_url=env['R2_ENDPOINT'],
                 aws_access_key_id=env['R2_ACCESS_KEY_ID'],
                 aws_secret_access_key=env['R2_SECRET_ACCESS_KEY'])

henv = load_env('/root/.hermes/.env')
key = henv.get('HERMES_CUSTOM_ARK_CN_BEIJING_VOLCES_COM_API_KEY')

path = '/root/novels/the-deep-end/chapters/ch021.md'
title, content = parse_chapter(path)
text = ' '.join(content)
hl = None
for attempt in range(5):
    try:
        hl = llm_highlight(key, title, text)
        if hl and hl.strip():
            break
    except Exception as e:
        print(f"attempt {attempt}: {e}")
if not hl or not hl.strip():
    hl = content[0][:120]
print(f"ch21 hl: {hl!r}")

BID = 1557
obj = json.loads(c.get_object(Bucket=env['R2_BUCKET'], Key=f"{BID}/21.json")['Body'].read())
obj['highlight'] = hl
c.put_object(Bucket=env['R2_BUCKET'], Key=f"{BID}/21.json",
             Body=json.dumps(obj, ensure_ascii=False).encode(),
             ContentType='application/json',
             CacheControl='public, max-age=31536000, immutable')
got = json.loads(c.get_object(Bucket=env['R2_BUCKET'], Key=f"{BID}/21.json")['Body'].read())
print("verify:", got['chapter_id'], got['title'], '| highlight:', got['highlight'][:60])
