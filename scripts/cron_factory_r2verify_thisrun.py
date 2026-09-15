#!/usr/bin/env python3
"""Independent R2 read-back for book 1558 half-saint-half-fool."""
import json, boto3

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
    aws_access_key_id=env['R2_ACCESS_KEY_ID'], aws_secret_access_key=env['R2_SECRET_ACCESS_KEY'])
B = env['R2_BUCKET']
books = json.loads(client.get_object(Bucket=B, Key='books.json')['Body'].read())
entry = [b for b in books if b['id'] == 1558][0]
print('BOOKS_ENTRY', json.dumps({k: entry.get(k) for k in ('id','slug','title','author','lang','total_chapters','category','tags')}, ensure_ascii=False))
cat = json.loads(client.get_object(Bucket=B, Key='catalog_1558.json')['Body'].read())
chapters = cat.get('chapters', [])
print('CATALOG_COUNT', len(chapters))
print('CATALOG_KEYS_OK', all('chapter_id' in c and isinstance(c['chapter_id'], int) for c in chapters))
print('FIRST_CH', chapters[0])
print('LAST_CH', chapters[-1])
ch1 = json.loads(client.get_object(Bucket=B, Key='1558/1.json')['Body'].read())
ch28 = json.loads(client.get_object(Bucket=B, Key='1558/28.json')['Body'].read())
print('CH1_HL', bool(ch1.get('highlight')), '| CH1_PARAS', len(ch1.get('content', [])))
print('CH28_HL', bool(ch28.get('highlight')), '| CH28_PARAS', len(ch28.get('content', [])))
print('ALL_OK', entry.get('lang') == 'english' and entry.get('total_chapters') == 28 and len(chapters) == 28)
