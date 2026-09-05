#!/usr/bin/env python3
"""Upload Killjoy (book id 1327) to R2 'novel-data' — Phase 6B manual uploader (boto3).
Parses chapters from /root/novels/killjoy/chapters/, generates highlights via
Volces ARK LLM, PUTs chapter/catalog/books objects."""
import os, re, json, time, urllib.request
import boto3
from dotenv import load_dotenv

NOVEL_DIR = "/root/novels/killjoy"
BOOK_ID = 1327
SLUG = "killjoy"
TITLE = "Killjoy"

load_dotenv("/root/novel-site/.env")
s3 = boto3.client("s3", endpoint_url=os.environ["R2_ENDPOINT"],
                  aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
                  aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"], region_name="auto")
BUCKET = os.environ["R2_BUCKET"]

# --- load LLM key
llm_key = None
with open("/root/.hermes/.env") as f:
    for line in f:
        line = line.strip()
        if line.startswith("HERMES_CUSTOM_ARK_CN_BEIJING_VOLCES_COM_API_KEY"):
            llm_key = line.split("=", 1)[1].strip().strip('"').strip("'")
assert llm_key, "LLM key not found"
LLM_BASE = "https://ark.cn-beijing.volces.com/api/v3"
LLM_MODEL = "deepseek-v4-flash-ga-260731"

# --- parse chapters
def parse_chapter(path):
    with open(path) as f:
        raw = f.read()
    lines = raw.split("\n")
    assert lines[0].startswith("# Chapter"), f"bad H1 in {path}: {lines[0][:50]}"
    title = lines[0][2:].strip()
    body = "\n".join(lines[1:])
    paras = [re.sub(r"\s+", " ", b.strip()) for b in re.split(r"\n\s*\n", body)]
    paras = [p for p in paras if p and not p.startswith("#")]
    return title, paras

chapters = []
for n in range(1, 25):
    p = f"{NOVEL_DIR}/chapters/ch{n:03d}.md"
    title, paras = parse_chapter(p)
    chapters.append({"n": n, "title": title, "content": paras})
    print(f"parsed ch{n:02d}: {title}  ({len(paras)} paras, {sum(len(x.split()) for x in paras)} words)")

# --- highlights via LLM
def llm_highlight(title, content):
    prompt = ("Write one short highlight line for this web-novel chapter. "
              "Rules: single line, max 25 words, no quotation marks, no meta-language "
              "(no 'in this chapter', no 'this chapter'). Punchy, teasing, emotional.\n\n"
              f"Chapter title: {title}\n\nChapter opening:\n" + " ".join(content[:6])[:900])
    body = json.dumps({"model": LLM_MODEL, "messages": [{"role": "user", "content": prompt}],
                       "max_tokens": 80, "temperature": 0.8}).encode()
    req = urllib.request.Request(f"{LLM_BASE}/chat/completions", data=body,
                                 headers={"Content-Type": "application/json", "Authorization": f"Bearer {llm_key}"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read())
            return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"  llm retry {attempt+1}: {e}")
            time.sleep(3)
    return ""

for c in chapters:
    c["highlight"] = llm_highlight(c["title"], c["content"])
    print(f"  highlight ch{c['n']:02d}: {c['highlight'][:90]}")
    time.sleep(0.5)

def put_json(key, obj, cache_control):
    s3.put_object(Bucket=BUCKET, Key=key, Body=json.dumps(obj, ensure_ascii=False).encode(),
                  ContentType="application/json", CacheControl=cache_control)
    print(f"PUT {key}")

# --- books.json
books = json.loads(s3.get_object(Bucket=BUCKET, Key="books.json")["Body"].read())
new_entry = {
    "id": BOOK_ID, "slug": SLUG, "title": TITLE, "author": "Apex Shaw",
    "category": "Satire / Contemporary / BookTok",
    "intro": ("Juno Reyes dies on open-mic stages and writes Chase Wilder's jokes in secret. "
              "By night she is Killjoy, the anonymous account that roasts the industry's fake saints. "
              "When the nicest man in comedy steals her best bit and buries the woman who accused him, "
              "Juno has to decide which mask gets to live. She wrote his jokes. She unmasked his empire. "
              "The set is hers now."),
    "total_chapters": 24, "lang": "english", "tags": []
}
books = [b for b in books if b["id"] != BOOK_ID]
books.append(new_entry)
put_json("books.json", books, "no-cache, no-store, must-revalidate")
print(f"books.json updated: {len(books)} books, id {BOOK_ID} added")

# --- catalog
catalog = {"book_id": BOOK_ID, "slug": SLUG, "title": TITLE,
           "chapters": [{"chapter_id": c["n"], "title": c["title"]} for c in chapters]}
put_json(f"catalog_{BOOK_ID}.json", catalog, "public, max-age=31536000, immutable")

# --- chapters
for c in chapters:
    obj = {"book_id": BOOK_ID, "chapter_id": c["n"], "title": c["title"],
           "content": c["content"], "highlight": c["highlight"]}
    put_json(f"{BOOK_ID}/{c['n']}.json", obj, "public, max-age=31536000, immutable")
print(f"{len(chapters)} chapter objects uploaded")
print("DONE")
