#!/usr/bin/env python3
"""Manual R2 upload for GILDED BURNING (Phase 6B): preserves/replaces highlights, generates new via LLM.
Usage: python3 upload_gilded.py --id 1334 --dir gilded-burning
"""
import json, os, re, sys, time, yaml, argparse, urllib.request
from pathlib import Path
import boto3

NOVELS_DIR = Path("/root/novels")
ENV_FILE = Path("/root/novel-site/.env")
HERMES_ENV = Path("/root/.hermes/.env")
BOOKS_KEY = "books.json"

def load_env(path):
    env = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line: continue
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env

def parse_chapter(text):
    lines = text.strip().split("\n")
    title = lines[0].lstrip("# ").strip() if lines and lines[0].startswith("#") else "Chapter"
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip() and not p.strip().startswith("#")]
    return title, paragraphs

def get_llm_config():
    env = load_env(HERMES_ENV)
    key = env.get("HERMES_CUSTOM_ARK_CN_BEIJING_VOLCES_COM_API_KEY", "").strip()
    return "https://ark.cn-beijing.volces.com/api/v3", key, "deepseek-v4-flash-ga-260731"

def generate_highlight(title, content_text, api_base, api_key, model):
    text = content_text[:5000] + ("..." if len(content_text) > 5000 else "")
    prompt = f"""You are a masterful book editor. Generate a single compelling "chapter highlight" line for this novel chapter.
Rules:
- One sentence, max 25 words
- Must be eye-catching and hook the reader's curiosity
- Can be a striking quote from the text OR a teasing summary of the core suspense
- Do NOT wrap in quotes
- Do NOT start with "In this chapter" or similar meta-language

Chapter title: {title}
Chapter text:
{text}"""
    body = json.dumps({'model': model, 'messages': [{'role': 'user', 'content': prompt}], 'max_tokens': 60, 'temperature': 0.7}).encode()
    req = urllib.request.Request(f'{api_base}/chat/completions', data=body,
        headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {api_key}'})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                result = json.loads(resp.read())
            hl = result['choices'][0]['message']['content'].strip().strip('"').strip("'")
            hl = re.sub(r'^(?:本章金句|核心悬念)[：:]\s*', '', hl).strip()
            return hl
        except Exception as e:
            print(f"  hl retry {attempt+1}: {e}")
            time.sleep(5)
    return ""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", type=int, required=True)
    ap.add_argument("--dir", required=True)
    ap.add_argument("--skip-highlights", action="store_true")
    args = ap.parse_args()

    env = load_env(ENV_FILE)
    client = boto3.client('s3', endpoint_url=env['R2_ENDPOINT'],
        aws_access_key_id=env['R2_ACCESS_KEY_ID'], aws_secret_access_key=env['R2_SECRET_ACCESS_KEY'])
    bucket = env['R2_BUCKET']
    book_id = args.id
    project_dir = NOVELS_DIR / args.dir

    # --- meta ---
    with open(project_dir / "novel-project.yaml", encoding="utf-8") as f:
        meta = yaml.safe_load(f)["meta"]
    slug = re.sub(r'&', 'and', args.dir)
    slug = re.sub(r'[^a-z0-9]+', '-', slug.lower()).strip('-')

    # --- read books.json ---
    books = json.loads(client.get_object(Bucket=bucket, Key=BOOKS_KEY)['Body'].read())
    existing = next((b for b in books if b['id'] == book_id), None)
    old_cat = None
    if existing is not None:
        try:
            old_cat = json.loads(client.get_object(Bucket=bucket, Key=f'catalog_{book_id}.json')['Body'].read())
        except Exception:
            old_cat = None
    print(f"book_id={book_id} slug={slug} existing={existing is not None}")

    # --- parse chapters ---
    ch_files = sorted((project_dir / "chapters").glob("ch*.md"))
    chapters = []
    for f in ch_files:
        m = re.search(r'ch(\d+)', f.name)
        cid = int(m.group(1)) if m else 0
        title, paras = parse_chapter(f.read_text(encoding="utf-8"))
        chapters.append({"id": cid, "title": title, "content": paras, "file": f.name})
    chapters.sort(key=lambda c: c["id"])
    print(f"chapters parsed: {len(chapters)}")

    # --- map old highlights by first-paragraph prefix ---
    old_hl = {}
    if old_cat:
        for old_ch in old_cat.get("chapters", []):
            oid = old_ch["chapter_id"]
            try:
                obj = json.loads(client.get_object(Bucket=bucket, Key=f'{book_id}/{oid}.json')['Body'].read())
                if obj.get("content") and obj.get("highlight"):
                    old_hl[obj["content"][0][:80]] = obj["highlight"]
            except Exception:
                pass
    print(f"old highlights mapped: {len(old_hl)}")

    # --- highlights ---
    api_base, api_key, model = get_llm_config()
    if args.skip_highlights:
        highlights = {c["id"]: "" for c in chapters}
    else:
        highlights = {}
        for c in chapters:
            prefix = c["content"][0][:80] if c["content"] else ""
            if prefix in old_hl:
                highlights[c["id"]] = old_hl[prefix]
                print(f"ch{c['id']}: reused old highlight")
            else:
                hl = generate_highlight(c["title"], "\n\n".join(c["content"]), api_base, api_key, model)
                highlights[c["id"]] = hl
                print(f"ch{c['id']}: generated -> {hl[:60]}")
                time.sleep(1)
        print(f"highlights done: {sum(1 for v in highlights.values() if v)}/{len(chapters)}")

    # --- upload chapter objects ---
    for c in chapters:
        payload = json.dumps({"book_id": book_id, "chapter_id": c["id"], "title": c["title"],
                              "content": c["content"], "highlight": highlights.get(c["id"], "")},
                             ensure_ascii=False).encode()
        client.put_object(Bucket=bucket, Key=f'{book_id}/{c["id"]}.json', Body=payload,
            ContentType="application/json", CacheControl="public, max-age=31536000, immutable")
    print("chapter objects uploaded")

    # --- catalog ---
    cat_payload = json.dumps({"book_id": book_id,
        "chapters": [{"chapter_id": c["id"], "title": c["title"]} for c in chapters]}, ensure_ascii=False).encode()
    client.put_object(Bucket=bucket, Key=f'catalog_{book_id}.json', Body=cat_payload,
        ContentType="application/json", CacheControl="public, max-age=31536000, immutable")
    print("catalog uploaded")

    # --- books.json entry ---
    intro = meta.get("premise", "")[:200] or meta.get("logline", "")[:200]
    entry = {
        "id": book_id, "slug": slug, "title": meta["title"], "author": meta["author"],
        "category": meta["genre"],
        "intro": intro,
        "total_chapters": len(chapters),
        "lang": "english",
        "tags": ["Art Crime Thriller", "Mystery", "Suspense", "Romance", "Female Lead", "Revenge", "BookTok"],
    }
    books = [b for b in books if b["id"] != book_id]
    books.append(entry)
    books.sort(key=lambda b: b["id"])
    books_payload = json.dumps(books, ensure_ascii=False).encode()
    client.put_object(Bucket=bucket, Key=BOOKS_KEY, Body=books_payload,
        ContentType="application/json", CacheControl="no-cache, no-store, must-revalidate")
    print(f"books.json updated: {len(books)} entries")

    print("DONE")

if __name__ == "__main__":
    main()
