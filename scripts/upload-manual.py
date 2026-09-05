#!/usr/bin/env python3
"""Manual R2 uploader for novel factory books (Phase 6B).

Preserves the official uploader's contract but generates highlights via the
working LLM config (ark.cn-beijing.volces.com) instead of the 401-ing
config.yaml api_key path.

Usage: python3 upload-manual.py --id N --dir /root/novels/<slug> --slug <slug>
"""
import argparse, json, os, re, sys, time, urllib.request, urllib.error

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
    """H1 -> title (verbatim, e.g. 'Chapter 3: The Mutiny in the Kitchen'),
    non-# paragraphs -> content list. Skips blank lines and any # lines."""
    title, content = None, []
    for line in open(path, encoding='utf-8'):
        line = line.rstrip('\n')
        if title is None:
            if line.startswith('# '):
                title = line[2:].strip()
                continue
            if not line.strip():
                continue
            # tolerate a missing H1: first non-empty line becomes title
            title = line.strip()
            continue
        if not line.strip():
            continue
        if line.startswith('#'):
            continue  # uploader drops hash-leading lines; we mirror that
        content.append(line.strip())
    if title is None:
        raise ValueError(f"no H1 in {path}")
    return title, content

def llm_highlight(key, chapter_title, text):
    """One-line chapter highlight <=25 words via deepseek-v4-flash."""
    body = json.dumps({
        "model": "deepseek-v4-flash-ga-260731",
        "messages": [
            {"role": "system", "content": "You write one-line teaser highlights for web novel chapters. Rules: English, one sentence, under 25 words, present tense, tease the chapter's emotional peak, no quotes, no em dashes, no meta-language like 'in this chapter', no character names unless essential. Output ONLY the highlight sentence."},
            {"role": "user", "content": f"Chapter title: {chapter_title}\n\nChapter text (first 1400 chars):\n{text[:1400]}\n\nHighlight:"},
        ],
        "max_tokens": 60,
        "temperature": 0.7,
    })
    req = urllib.request.Request(
        "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
        data=body.encode(),
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {key}"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                out = json.loads(r.read().decode())
            hl = out["choices"][0]["message"]["content"].strip().strip('"').strip("'")
            hl = hl.split('\n')[0].strip()
            if len(hl) > 200:
                hl = hl[:197] + "..."
            return hl
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 3:
                time.sleep(5 * (attempt + 1))
                continue
            raise
        except Exception as e:
            if attempt < 3:
                time.sleep(3)
                continue
            raise
    raise RuntimeError("highlight LLM failed")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", type=int, required=True)
    ap.add_argument("--dir", required=True)
    ap.add_argument("--slug", required=True)
    ap.add_argument("--skip-highlights", action="store_true")
    ap.add_argument("--title", default=None)
    ap.add_argument("--author", default="Apex Shaw")
    ap.add_argument("--category", default="")
    ap.add_argument("--intro", default="")
    ap.add_argument("--tags", default="")
    args = ap.parse_args()

    env = load_env("/root/novel-site/.env")
    bucket = env["R2_BUCKET"]
    import boto3
    c = boto3.client('s3', endpoint_url=env['R2_ENDPOINT'],
        aws_access_key_id=env['R2_ACCESS_KEY_ID'],
        aws_secret_access_key=env['R2_SECRET_ACCESS_KEY'])

    chapters_dir = os.path.join(args.dir, "chapters")
    files = sorted(f for f in os.listdir(chapters_dir) if re.fullmatch(r'ch\d{3}\.md', f))
    if not files:
        sys.exit("no chNNN.md files found")
    n = int(re.search(r'ch(\d{3})', files[0]).group(1))
    parsed = {}
    for f in files:
        m = re.search(r'ch(\d{3})\.md', f)
        num = int(m.group(1))
        title, content = parse_chapter(os.path.join(chapters_dir, f))
        parsed[num] = (title, content)
    nums = sorted(parsed)
    print(f"parsed {len(nums)} chapters: {nums[0]}..{nums[-1]}")

    # chapter title prefix check: files H1 should already contain 'Chapter N:'
    for num in nums:
        t = parsed[num][0]
        if not t.startswith(f"Chapter {num}:"):
            print(f"  !! ch{num:03d} H1 missing prefix: {t!r}")

    key = None
    try:
        henv = load_env("/root/.hermes/.env")
        key = henv.get("HERMES_CUSTOM_ARK_CN_BEIJING_VOLCES_COM_API_KEY")
    except Exception:
        pass
    if not key:
        print("WARNING: no LLM key found; highlights will be empty")
        key = None

    # highlights
    highlights = {}
    if not args.skip_highlights and key:
        for num in nums:
            t, content = parsed[num]
            text = " ".join(content)
            hl = llm_highlight(key, t, text)
            highlights[num] = hl
            print(f"  ch{num:03d} hl: {hl}")
            time.sleep(0.4)
    else:
        for num in nums:
            highlights[num] = parsed[num][1][0][:120] if parsed[num][1] else ""

    IMM = {"CacheControl": "public, max-age=31536000, immutable"}

    # 1. chapter objects
    for num in nums:
        title, content = parsed[num]
        obj = {"book_id": args.id, "chapter_id": num, "title": title,
               "content": content, "highlight": highlights[num]}
        c.put_object(Bucket=bucket, Key=f"{args.id}/{num}.json",
                     Body=json.dumps(obj, ensure_ascii=False).encode(),
                     ContentType="application/json", **IMM)
    print(f"uploaded {len(nums)} chapter objects")

    # 2. catalog
    catalog = {"book_id": args.id,
               "chapters": [{"chapter_id": num, "title": parsed[num][0]} for num in nums]}
    c.put_object(Bucket=bucket, Key=f"catalog_{args.id}.json",
                 Body=json.dumps(catalog, ensure_ascii=False).encode(),
                 ContentType="application/json", **IMM)
    print("uploaded catalog")

    # 3. books.json update (replace same id, sort by id, no-cache)
    books = json.loads(c.get_object(Bucket=bucket, Key='books.json')['Body'].read())
    entry = {
        "id": args.id,
        "slug": args.slug,
        "title": args.title or f"BOOK {args.id}",
        "author": args.author,
        "category": args.category,
        "intro": args.intro,
        "total_chapters": len(nums),
        "lang": "english",
        "tags": [t.strip() for t in args.tags.split(",") if t.strip()],
    }
    books = [b for b in books if b.get("id") != args.id]
    books.append(entry)
    books.sort(key=lambda b: b.get("id", 0))
    c.put_object(Bucket=bucket, Key='books.json',
                 Body=json.dumps(books, ensure_ascii=False).encode(),
                 ContentType="application/json",
                 CacheControl="no-cache, no-store, must-revalidate")
    print(f"books.json updated: id {args.id}, slug {args.slug}, total_chapters {len(nums)}")

    # 4. verify
    for num in [nums[0], nums[-1]]:
        got = json.loads(c.get_object(Bucket=bucket, Key=f"{args.id}/{num}.json")['Body'].read())
        assert got["chapter_id"] == num and got["title"] == parsed[num][0], f"verify failed ch{num}"
        assert got.get("highlight"), f"missing highlight ch{num}"
    cat = json.loads(c.get_object(Bucket=bucket, Key=f"catalog_{args.id}.json")['Body'].read())
    assert len(cat["chapters"]) == len(nums)
    assert all(isinstance(x["chapter_id"], int) for x in cat["chapters"])
    print("R2 verify OK")

if __name__ == "__main__":
    main()
