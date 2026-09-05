#!/usr/bin/env python3
"""Upload UNBURN ME to R2 (Phase 6B manual path, highlight-preserving).

Reads chapters from /root/novels/unburn-me/chapters/ (H1 -> title, paragraphs -> content),
generates highlights via Ark LLM for new chapters, PUTs {id}/{n}.json + catalog_{id}.json
+ updates books.json. Also renames old chapters' highlights when a first-paragraph prefix matches.
"""
import json, os, re, sys, time, urllib.request
from pathlib import Path
import boto3

SLUG = "unburn-me"
BOOK_ID = int(sys.argv[1]) if len(sys.argv) > 1 else 1343
NOVELS_DIR = Path("/root/novels/unburn-me")
ENV = {}
for line in Path("/root/novel-site/.env").read_text().splitlines():
    line = line.strip()
    if line and "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        ENV[k.strip()] = v.strip().strip('"').strip("'")
HERMES_ENV = {}
for line in Path("/root/.hermes/.env").read_text().splitlines():
    line = line.strip()
    if line and "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        HERMES_ENV[k.strip()] = v.strip().strip('"').strip("'")

s3 = boto3.client(
    "s3",
    endpoint_url=ENV["R2_ENDPOINT"],
    aws_access_key_id=ENV["R2_ACCESS_KEY_ID"],
    aws_secret_access_key=ENV["R2_SECRET_ACCESS_KEY"],
    region_name="auto",
)
BUCKET = ENV["R2_BUCKET"]

def get_json(key):
    try:
        obj = s3.get_object(Bucket=BUCKET, Key=key)
        return json.loads(obj["Body"].read().decode())
    except Exception:
        return None

def put_json(key, data, cache_control="public, max-age=31536000, immutable"):
    s3.put_object(
        Bucket=BUCKET, Key=key,
        Body=json.dumps(data, ensure_ascii=False).encode(),
        ContentType="application/json; charset=utf-8",
        CacheControl=cache_control,
    )
    print(f"PUT {key}")

def parse_chapters():
    chapters = []
    for p in sorted(NOVELS_DIR.glob("chapters/ch*.md")):
        text = p.read_text(encoding="utf-8")
        lines = text.split("\n")
        # H1 first line
        title = ""
        for ln in lines:
            if ln.startswith("# "):
                title = ln[2:].strip()
                break
        content = []
        for ln in lines:
            if ln.startswith("#"):
                continue
            if ln.strip():
                content.append(ln.strip())
        chapters.append({"num": int(p.stem.replace("ch", "")), "title": title, "content": content})
    chapters.sort(key=lambda c: c["num"])
    return chapters

def llm_highlight(title, first_para):
    api_key = HERMES_ENV.get("HERMES_CUSTOM_ARK_CN_BEIJING_VOLCES_COM_API_KEY", "")
    if not api_key:
        return None
    prompt = (f"Write ONE line chapter highlight for an English web novel, max 25 words, "
              f"no quotes, no meta-language like 'In this chapter'. Chapter title: {title}. "
              f"First lines: {first_para[:300]}")
    body = json.dumps({
        "model": "deepseek-v4-flash-ga-260731",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 60,
        "temperature": 0.7,
    }).encode()
    req = urllib.request.Request(
        "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
        data=body,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read().decode())
            return data["choices"][0]["message"]["content"].strip().strip('"').strip("'")
    except Exception as e:
        print(f"  LLM error: {e}")
        return None

def main():
    books = get_json("books.json") or []
    existing = get_json(f"catalog_{BOOK_ID}.json")
    old_chapters = existing.get("chapters", []) if existing else []
    old_content_by_prefix = {}
    for oc in old_chapters:
        if oc.get("content"):
            old_content_by_prefix[oc["content"][0][:80]] = oc

    chapters = parse_chapters()
    print(f"Parsed {len(chapters)} chapters")

    highlights = {}
    for ch in chapters:
        prefix = ch["content"][0][:80] if ch["content"] else ""
        if prefix in old_content_by_prefix:
            highlights[ch["num"]] = old_content_by_prefix[prefix].get("highlight", "")
            print(f"  ch{ch['num']}: kept old highlight")
        else:
            h = llm_highlight(ch["title"], ch["content"][0] if ch["content"] else "")
            highlights[ch["num"]] = h or ""
            print(f"  ch{ch['num']}: new highlight -> {h}")

    total_words = sum(len(" ".join(c["content"]).split()) for c in chapters)

    # chapter objects
    for ch in chapters:
        data = {
            "book_id": BOOK_ID,
            "chapter_id": str(ch["num"]),
            "title": f"Chapter {ch['num']}: {ch['title']}",
            "content": ch["content"],
            "highlight": highlights.get(ch["num"], ""),
        }
        put_json(f"{BOOK_ID}/{ch['num']}.json", data)

    # catalog
    catalog = {
        "book_id": BOOK_ID,
        "title": "UNBURN ME",
        "chapters": [
            {"chapter_id": str(ch["num"]), "title": f"Chapter {ch['num']}: {ch['title']}"}
            for ch in chapters
        ],
    }
    put_json(f"catalog_{BOOK_ID}.json", catalog)

    # books.json entry
    entry = next((b for b in books if b.get("id") == BOOK_ID), None)
    if entry is None:
        entry = {
            "id": BOOK_ID,
            "title": "UNBURN ME",
            "author": "Apex Shaw",
            "slug": SLUG,
            "language": "english",
            "lang": "english",
            "category": "Sci-Fi, Dystopia, Tech Thriller, Revenge, Female Lead, BookTok, Dark Satire",
            "intro": "Cancelled author Elara Quinn watches her bestselling novel get burned from everyone's memory in a live stream. Two years of silence later she joins HELIO, the memory platform that erased her, as a lowly content moderator - and starts saving pages one deletion at a time. But her quiet rebellion is really the setup for the biggest joke HELIO ever told: the day she hijacks the Burn Protocol and makes the whole world remember.",
            "total_chapters": len(chapters),
            "total_words": total_words,
        }
        books.append(entry)
    else:
        entry["total_chapters"] = len(chapters)
        entry["total_words"] = total_words
        entry["slug"] = SLUG

    put_json("books.json", books, cache_control="no-cache, no-store, must-revalidate")
    print(f"DONE. id={BOOK_ID} slug={SLUG} chapters={len(chapters)} words={total_words}")

if __name__ == "__main__":
    main()
