#!/usr/bin/env python3
"""Phase 6B: manual R2 upload for THE TOUCH TEST (id 1345).
- Parses chapters (H1 -> title, plain paragraphs -> content)
- Generates one-line highlights via Ark LLM for every chapter (new book, nothing to preserve)
- PUT {id}/{n}.json + catalog_{id}.json + updated books.json
"""
import json, os, re, sys, glob, time
import urllib.request

# ---------- creds ----------
env = {}
for line in open('/root/novel-site/.env'):
    line = line.strip()
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        env[k] = v.strip().strip('"').strip("'")

api_key = None
for line in open('/root/.hermes/.env'):
    line = line.strip()
    if line.startswith('HERMES_CUSTOM_ARK_CN_BEIJING_VOLCES_COM_API_KEY='):
        api_key = line.split('=', 1)[1].strip().strip('"').strip("'")
assert api_key, "API key not found"

import boto3
from botocore.config import Config
s3 = boto3.client('s3', endpoint_url=env['R2_ENDPOINT'],
                  aws_access_key_id=env['R2_ACCESS_KEY_ID'],
                  aws_secret_access_key=env['R2_SECRET_ACCESS_KEY'],
                  region_name='auto', config=Config(signature_version='s3v4'))
bucket = env['R2_BUCKET']

BOOK_ID = 1345
SLUG = 'the-touch-test'
TITLE = 'THE TOUCH TEST'
AUTHOR = 'Apex Shaw'
CATEGORY = "Sensory Thriller, Contemporary Romance, Influencer Drama, Friendship Revenge, Female Lead, BookTok, Disability Rep"
TAGS = ["Romance", "Thriller", "Contemporary", "Female Lead", "Disability Rep", "Influencer"]
INTRO = ("Iris Chen, a blind ASMR creator, can read people through touch, scent, and vibration the way "
         "sighted people read faces. Her Touch Test videos prove fakes, expose filters, unmask liars — and "
         "go viral. But her childhood best friend Renata is the internet's most beloved fake: a beauty "
         "influencer whose entire empire is built on a lie. When the same scandal that made Iris famous starts "
         "pointing at Renata, Iris has to choose between the truth that made her and the only friend who ever "
         "saw her as more than her disability. She can't see your face. She can still catch your lie.")

# ---------- parse chapters ----------
def parse_chapters(dirpath):
    chs = {}
    for f in sorted(glob.glob(os.path.join(dirpath, 'ch*.md'))):
        m = re.search(r'ch(\d+)\.md$', f)
        if not m:
            continue
        n = int(m.group(1))
        text = open(f, encoding='utf-8').read()
        lines = [l.rstrip() for l in text.split('\n')]
        title = None
        paras = []
        for l in lines:
            if l.startswith('#'):
                if title is None:
                    title = l.lstrip('#').strip()
                continue
            if l.strip():
                paras.append(l.strip())
        assert title, f"{f}: no H1"
        assert paras, f"{f}: no body"
        chs[n] = {'title': title, 'content': paras}
    return chs

# ---------- LLM highlight ----------
def llm_highlight(chapter_text):
    body = chapter_text[:1500]
    payload = {
        "model": "deepseek-v4-flash-ga-260731",
        "messages": [
            {"role": "system", "content": "You write one-line chapter highlights for a web novel. Output ONLY the highlight: one sentence, max 25 words, no quotation marks, no meta-language like 'In this chapter', no labels. Make it teasing, emotional, or punchy."},
            {"role": "user", "content": f"Chapter text:\n{body}\n\nHighlight:"}
        ],
        "max_tokens": 60,
        "temperature": 0.8
    }
    req = urllib.request.Request(
        "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.loads(r.read().decode())
    return data["choices"][0]["message"]["content"].strip()

# ---------- run ----------
def main():
    chapters = parse_chapters('/root/novels/the-touch-test/chapters')
    ns = sorted(chapters.keys())
    print(f"parsed {len(ns)} chapters: {ns[0]}..{ns[-1]}")
    assert ns == list(range(1, len(ns) + 1)), "chapter numbers not contiguous"
    for n in ns:
        title, content = chapters[n]['title'], chapters[n]['content']
        wc = sum(len(c.split()) for c in content)
        print(f"  ch{n}: {wc} words | {title}")
        if wc < 1300:
            print(f"  !! WARNING ch{n} under 1300 words")

    # highlights via LLM
    print("generating highlights...")
    for i, n in enumerate(ns):
        hl = llm_highlight('\n'.join(chapters[n]['content']))
        chapters[n]['highlight'] = hl
        print(f"  ch{n}: {hl[:60]}")
        time.sleep(0.3)

    # PUT chapter objects
    print("uploading chapter objects...")
    for n in ns:
        obj = {
            "book_id": BOOK_ID,
            "chapter_id": n,
            "title": chapters[n]['title'],
            "content": chapters[n]['content'],
            "highlight": chapters[n]['highlight'],
        }
        s3.put_object(Bucket=bucket, Key=f"{BOOK_ID}/{n}.json",
                      Body=json.dumps(obj, ensure_ascii=False).encode(),
                      ContentType='application/json',
                      CacheControl='public, max-age=31536000, immutable')
    print(f"  uploaded {len(ns)} chapter objects")

    # catalog
    catalog = {"book_id": BOOK_ID, "chapters": [
        {"chapter_id": n, "title": chapters[n]['title']} for n in ns]}
    s3.put_object(Bucket=bucket, Key=f"catalog_{BOOK_ID}.json",
                  Body=json.dumps(catalog, ensure_ascii=False).encode(),
                  ContentType='application/json',
                  CacheControl='public, max-age=31536000, immutable')
    print("  uploaded catalog")

    # books.json
    books = json.loads(s3.get_object(Bucket=bucket, Key='books.json')['Body'].read().decode())
    entry = {"id": BOOK_ID, "slug": SLUG, "title": TITLE, "author": AUTHOR,
             "category": CATEGORY, "intro": INTRO, "total_chapters": len(ns),
             "lang": "english", "tags": TAGS}
    books = [b for b in books if b.get('id') != BOOK_ID] + [entry]
    s3.put_object(Bucket=bucket, Key='books.json',
                  Body=json.dumps(books, ensure_ascii=False).encode(),
                  ContentType='application/json',
                  CacheControl='no-cache, no-store, must-revalidate')
    print("  uploaded books.json entry")

    # verify
    print("--- verify ---")
    b = json.loads(s3.get_object(Bucket=bucket, Key='books.json')['Body'].read().decode())
    me = [x for x in b if x.get('id') == BOOK_ID][0]
    print("books.json entry:", me['id'], me['slug'], me['total_chapters'], me['lang'])
    cat = json.loads(s3.get_object(Bucket=bucket, Key=f'catalog_{BOOK_ID}.json')['Body'].read().decode())
    print("catalog chapters:", len(cat['chapters']), "first:", cat['chapters'][0])
    c1 = json.loads(s3.get_object(Bucket=bucket, Key=f'{BOOK_ID}/1.json')['Body'].read().decode())
    print("ch1 keys:", sorted(c1.keys()), "| highlight:", c1.get('highlight', '')[:50])
    cn = json.loads(s3.get_object(Bucket=bucket, Key=f'{BOOK_ID}/{len(ns)}.json')['Body'].read().decode())
    print(f"ch{len(ns)} title:", cn['title'])
    print("ALL R2 UPLOADS VERIFIED")

if __name__ == '__main__':
    main()
