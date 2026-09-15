#!/usr/bin/env python3
"""Inspect recent book entries + word-count samples from R2."""
import json, os, boto3
def load_env(path):
    env = {}
    for line in open(path, encoding='utf-8'):
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        env[k] = v.strip().strip('"').strip("'")
    return env
env = load_env('/root/novel-site/.env')
c = boto3.client('s3', endpoint_url=env['R2_ENDPOINT'],
    aws_access_key_id=env['R2_ACCESS_KEY_ID'],
    aws_secret_access_key=env['R2_SECRET_ACCESS_KEY'])
rbooks = json.loads(c.get_object(Bucket=env['R2_BUCKET'], Key='books.json')['Body'].read())
byid = sorted(rbooks, key=lambda b: b.get('id', 0))
# full entry of 1483
b1483 = [b for b in byid if b.get('id') == 1483][0]
print("FULL ENTRY 1483:")
print(json.dumps(b1483, ensure_ascii=False, indent=1)[:900])
print()
print("--- recent books: id | total_chapters | title ---")
for b in byid[-12:]:
    print(f"{b.get('id')} | {b.get('total_chapters')} | {b.get('title','')[:45]}")
# word count samples for one book: first/mid/last chapter
for bid, label in [(1483, 'delusion-girl'), (1482, 'vanity-pilgrim')]:
    b = [x for x in byid if x.get('id') == bid][0]
    n = b.get('total_chapters', 0)
    nums = sorted(set([1, max(2, n // 2), n]))
    total = 0
    for num in nums:
        try:
            obj = json.loads(c.get_object(Bucket=env['R2_BUCKET'], Key=f'{bid}/{num}.json')['Body'].read())
            words = sum(len(p.split()) for p in obj.get('content', []))
            total += words
            print(f"  {label} ch{num}: {words} words")
        except Exception as e:
            print(f"  {label} ch{num}: ERR {e}")
    print(f"  {label} sampled avg ~{total // max(1,len(nums))} words/ch")
