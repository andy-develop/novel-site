#!/usr/bin/env python3
"""Regenerate highlights for specific chapters and re-PUT their R2 objects."""
import json, os, re, sys, time, urllib.request, urllib.error, boto3

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
KEY = None
for line in open("/root/.hermes/.env", encoding='utf-8'):
    line = line.strip()
    if line.startswith("HERMES_CUSTOM_ARK_CN_BEIJING_VOLCES_COM_API_KEY="):
        KEY = line.split("=", 1)[1].strip().strip('"').strip("'")

def llm_highlight(chapter_title, text, tries=4):
    body = json.dumps({
        "model": "deepseek-v4-flash-ga-260731",
        "messages": [
            {"role": "system", "content": "You write one-line teaser highlights for web novel chapters. Rules: English, one sentence, under 25 words, present tense, tease the chapter's emotional peak, no quotes, no em dashes, no meta-language like 'in this chapter', no character names unless essential, never invent events that are not in the provided text. Output ONLY the highlight sentence."},
            {"role": "user", "content": f"Chapter title: {chapter_title}\n\nChapter text (first 2000 chars):\n{text[:2000]}\n\nHighlight:"},
        ],
        "max_tokens": 60,
        "temperature": 0.7,
    })
    req = urllib.request.Request(
        "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
        data=body.encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {KEY}"})
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                out = json.loads(r.read().decode())
            hl = out["choices"][0]["message"]["content"].strip().strip('"').strip("'")
            return hl.split('\n')[0].strip()
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < tries - 1:
                time.sleep(5 * (attempt + 1))
                continue
            raise
        except Exception:
            if attempt < tries - 1:
                time.sleep(3)
                continue
            raise
    raise RuntimeError("llm failed")

book_id = int(sys.argv[1])
chapters_dir = sys.argv[2]
nums = [int(x) for x in sys.argv[3:]]

c = boto3.client('s3', endpoint_url=env['R2_ENDPOINT'],
    aws_access_key_id=env['R2_ACCESS_KEY_ID'],
    aws_secret_access_key=env['R2_SECRET_ACCESS_KEY'])

for n in nums:
    path = os.path.join(chapters_dir, f"ch{n:03d}.md")
    title, content = parse_chapter(path)
    hl = llm_highlight(title, " ".join(content))
    print(f"ch{n:03d} new highlight: {hl}")
    obj = {"book_id": book_id, "chapter_id": n, "title": title,
           "content": content, "highlight": hl}
    c.put_object(Bucket=env['R2_BUCKET'], Key=f"{book_id}/{n}.json",
        Body=json.dumps(obj, ensure_ascii=False).encode(),
        ContentType="application/json",
        CacheControl="public, max-age=31536000, immutable")
    # read-back
    got = c.get_object(Bucket=env['R2_BUCKET'], Key=f"{book_id}/{n}.json")
    back = json.loads(got['Body'].read().decode())
    assert back['highlight'] == hl, f"readback mismatch ch{n}"
    assert back['chapter_id'] == n
    print(f"ch{n:03d} readback OK")
print("done")
