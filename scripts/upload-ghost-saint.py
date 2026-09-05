#!/usr/bin/env python3
"""Manual R2 uploader for GHOST SAINT (Phase 6B of batch-novel-copilot).
Generates highlights via LLM (ark volces endpoint). New book: no old highlights.
"""
import boto3, json, os, re, sys, time, urllib.request

BASE_DIR = "/root/novels/ghost-saint"
BOOK_ID = 1336
SLUG = "ghost-saint"
TITLE = "Ghost Saint"
AUTHOR = "Apex Shaw"
CATEGORY = "Romance, Revenge, Influencer Fiction, Women's Fiction, BookTok, Comeback"
INTRO = ("Piper Lane is the invisible ghostwriter behind Aura Bailey, the Saint of "
         "Self-Care with eight million followers. Stranded with Aura's inner circle at "
         "a snowed-in influencer retreat, Piper keeps nine respectable people alive for "
         "three days, and they repay her by stealing her last script and firing her. "
         "Armed with receipts, a stolen manuscript, and a dead mentor's legacy, Piper "
         "unmasks every hypocrite one by one, until the Saint's own confession "
         "livestream becomes her downfall.")
TAGS = ["Romance", "Revenge", "Influencer Fiction", "Women's Fiction", "BookTok", "Comeback"]

def load_env(path):
    env = {}
    for line in open(path):
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env

def read_chapters():
    chs = []
    for n in range(1, 1000):
        p = os.path.join(BASE_DIR, "chapters", f"ch{n:03d}.md")
        if not os.path.exists(p):
            break
        text = open(p).read()
        lines = text.split('\n')
        title = None
        body = []
        for i, ln in enumerate(lines):
            if i == 0 and ln.startswith('# '):
                title = ln[2:].strip()
                continue
            if ln.strip().startswith('#'):
                continue  # drop stray headers
            if ln.strip():
                body.append(ln.strip())
        if not title:
            raise SystemExit(f"ch{n:03d}.md missing H1")
        chs.append({"n": n, "title": title, "content": body})
    return chs

def gen_highlight(ch, api_key):
    sample = " ".join(ch["content"][:8])[:1200]
    prompt = (f'Write ONE short line as the chapter highlight for the web novel '
              f'"GHOST SAINT" chapter "{ch["title"]}". At most 25 words. Tease action or '
              f'emotion. No quotes, no quotation marks, no meta language like "In this '
              f'chapter". Plain teaser sentence only.\nChapter opening: {sample}')
    body = json.dumps({
        "model": "deepseek-v4-flash-ga-260731",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 60, "temperature": 0.7
    }).encode()
    req = urllib.request.Request(
        "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
        data=body, headers={"Content-Type": "application/json",
                            "Authorization": f"Bearer {api_key}"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.loads(r.read())
            txt = data["choices"][0]["message"]["content"].strip()
            txt = txt.replace('"', '').replace("'", "").strip()
            return txt[:120]
        except Exception as e:
            if attempt == 2:
                print(f"  highlight LLM failed for ch{ch['n']}: {e}", file=sys.stderr)
                return None
            time.sleep(3)

def main():
    env = load_env("/root/novel-site/.env")
    s3 = boto3.client('s3', endpoint_url=env['R2_ENDPOINT'],
                      aws_access_key_id=env['R2_ACCESS_KEY_ID'],
                      aws_secret_access_key=env['R2_SECRET_ACCESS_KEY'])
    bucket = env['R2_BUCKET']
    ark_env = load_env("/root/.hermes/.env")
    api_key = ark_env.get("HERMES_CUSTOM_ARK_CN_BEIJING_VOLCES_COM_API_KEY")
    if not api_key:
        raise SystemExit("ARK API key not found")

    chs = read_chapters()
    print(f"chapters parsed: {len(chs)}")
    total_words = sum(len(" ".join(c["content"]).split()) for c in chs)
    print(f"total words: {total_words}")

    # 1. PUT chapter objects (highlight generated via LLM)
    for i, ch in enumerate(chs):
        hl = gen_highlight(ch, api_key)
        payload = json.dumps({"book_id": BOOK_ID, "chapter_id": ch["n"],
                              "title": ch["title"], "content": ch["content"],
                              "highlight": hl}, ensure_ascii=False)
        s3.put_object(Bucket=bucket, Key=f"{BOOK_ID}/{ch['n']}.json",
                      Body=payload.encode(), ContentType="application/json",
                      CacheControl="public, max-age=31536000, immutable")
        print(f"  uploaded {BOOK_ID}/{ch['n']}.json ({len(payload)} bytes) hl={'OK' if hl else 'NONE'}")
        time.sleep(0.3)

    # 2. PUT catalog
    cat = {"book_id": BOOK_ID,
           "chapters": [{"chapter_id": c["n"], "title": c["title"]} for c in chs]}
    s3.put_object(Bucket=bucket, Key=f"catalog_{BOOK_ID}.json",
                  Body=json.dumps(cat, ensure_ascii=False).encode(),
                  ContentType="application/json",
                  CacheControl="public, max-age=31536000, immutable")
    print("catalog uploaded")

    # 3. Update books.json entry
    books = json.loads(s3.get_object(Bucket=bucket, Key='books.json')['Body'].read())
    entry = {"id": BOOK_ID, "slug": SLUG, "title": TITLE, "author": AUTHOR,
             "category": CATEGORY, "intro": INTRO, "total_chapters": len(chs),
             "lang": "english", "tags": TAGS}
    books = [b for b in books if b.get('id') != BOOK_ID]
    books.append(entry)
    s3.put_object(Bucket=bucket, Key='books.json',
                  Body=json.dumps(books, ensure_ascii=False).encode(),
                  ContentType="application/json",
                  CacheControl="no-cache, no-store, must-revalidate")
    print("books.json updated")

    # 4. verify
    v = json.loads(s3.get_object(Bucket=bucket, Key=f'catalog_{BOOK_ID}.json')['Body'].read())
    assert len(v["chapters"]) == len(chs), "catalog count mismatch"
    for c in chs:
        o = json.loads(s3.get_object(Bucket=bucket, Key=f"{BOOK_ID}/{c['n']}.json")['Body'].read())
        assert o["chapter_id"] == c["n"] and o["title"] == c["title"]
        assert o.get("highlight"), f"missing highlight ch{c['n']}"
    vb = [b for b in json.loads(s3.get_object(Bucket=bucket, Key='books.json')['Body'].read()) if b.get('id')==BOOK_ID]
    assert vb and vb[0]["total_chapters"] == len(chs) and vb[0]["slug"] == SLUG and vb[0]["lang"] == "english"
    print("VERIFY OK:", len(chs), "chapters; books.json entry id", BOOK_ID, "slug", SLUG)

if __name__ == "__main__":
    main()
