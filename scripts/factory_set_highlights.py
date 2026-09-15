#!/usr/bin/env python3
"""Set specific chapter highlights directly and re-PUT R2 objects."""
import json, os, re, sys, boto3

def load_env(path):
    env = {}
    for line in open(path, encoding='utf-8'):
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        env[k] = v.strip().strip('"').strip("'")
    return env

def parse_chapter(path):
    title, content = None, []
    for line in open(path, encoding='utf-8'):
        line = line.rstrip('\n')
        if title is None:
            if line.startswith('# '):
                title = line[2:].strip()
                continue
            if not line.strip():
                continue
            title = line.strip()
            continue
        if not line.strip() or line.startswith('#'):
            continue
        content.append(line.strip())
    return title, content

env = load_env("/root/novel-site/.env")
book_id = int(sys.argv[1])
chapters_dir = sys.argv[2]
pairs = []  # (num, highlight)
for arg in sys.argv[3:]:
    n, hl = arg.split('=', 1)
    pairs.append((int(n), hl))

c = boto3.client('s3', endpoint_url=env['R2_ENDPOINT'],
    aws_access_key_id=env['R2_ACCESS_KEY_ID'],
    aws_secret_access_key=env['R2_SECRET_ACCESS_KEY'])

for n, hl in pairs:
    path = os.path.join(chapters_dir, f"ch{n:03d}.md")
    title, content = parse_chapter(path)
    obj = {"book_id": book_id, "chapter_id": n, "title": title,
           "content": content, "highlight": hl}
    c.put_object(Bucket=env['R2_BUCKET'], Key=f"{book_id}/{n}.json",
        Body=json.dumps(obj, ensure_ascii=False).encode(),
        ContentType="application/json",
        CacheControl="public, max-age=31536000, immutable")
    back = json.loads(c.get_object(Bucket=env['R2_BUCKET'], Key=f"{book_id}/{n}.json")['Body'].read().decode())
    assert back['highlight'] == hl and back['chapter_id'] == n
    print(f"ch{n:03d} set+readback OK: {hl}")
print("done")
