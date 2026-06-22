#!/usr/bin/env python3
"""Cold-start danmaku seeder — generates net-slang comments for the first 3 chapters of each English novel."""

import json, sys, os, time, random, subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SCRIPT_DIR))

# ---- Config ----
DANMAKU_PER_CHAPTER = 11  # 10-12 range
MIN_PARAGRAPH_CHARS = 120  # must match Vue component threshold
MODEL = os.environ.get("HL_MODEL", "Qwen/Qwen3-32B")
TIMEOUT = 180
R2_PUBLIC = "https://data.lyriq.space"

def get_llm_config():
    import yaml
    with open("/root/.hermes/config.yaml") as f:
        cfg = yaml.safe_load(f)
    m = cfg.get("model", {})
    return m.get("base_url", ""), m.get("api_key", ""), m.get("default", "")

API_BASE, API_KEY, _ = "", "", ""

def load_env():
    env_file = SCRIPT_DIR / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

def get_books():
    r = subprocess.run(["curl", "-s", f"{R2_PUBLIC}/books.json"], capture_output=True, text=True, timeout=15)
    return [b for b in json.loads(r.stdout) if b.get("lang") in ("english", "en")]

def get_catalog(book_id):
    r = subprocess.run(["curl", "-s", f"{R2_PUBLIC}/catalog_{book_id}.json"], capture_output=True, text=True, timeout=15)
    return json.loads(r.stdout)

def get_chapter(book_id, ch_id):
    r = subprocess.run(["curl", "-s", f"{R2_PUBLIC}/{book_id}/{ch_id}.json"], capture_output=True, text=True, timeout=15)
    return json.loads(r.stdout)

def get_r2_client():
    import boto3
    return boto3.client("s3",
        endpoint_url=os.environ["R2_ENDPOINT"],
        aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"])

def r2_key(book_id, ch_id):
    return f"danmaku/{book_id}/{ch_id}.json"

PROMPT_TEMPLATE = """You are a Gen-Z internet commenter on a novel reading app. Given a chapter's text (split into numbered paragraphs), generate exactly {count} fake danmaku (bullet comments) that readers might leave.

RULES:
- Use NET SLANG / casual English: "nah he did NOT just 💀", "bro is COOKED", "SHE ATE that", "holding my breath rn", "the way I just gasped", "ain't no way", "I'm screaming", "this hits different", etc.
- Match the paragraph content — react to specific moments, not generic praise
- paragraph_idx must point to an eligible paragraph (marked ✅)
- Mix reaction_type: mostly "text", some "emoji" (emoji goes in content field)
- Content max 140 chars. Be punchy and unhinged, not formal
- Return ONLY a JSON array, no markdown fences

Eligible paragraphs (✅ = long enough for danmaku):
{paragraphs_list}

Chapter text for context:
{chapter_text}

Return JSON array of {count} entries:
[{{"paragraph_idx": <int>, "content": "<string>", "reaction_type": "text"|"emoji"}}]"""

def call_llm(prompt):
    import urllib.request
    body = json.dumps({
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.9,
        "max_tokens": 2000,
    }).encode()
    req = urllib.request.Request(
        f"{API_BASE}/chat/completions",
        data=body,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"},
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        data = json.loads(resp.read())
    text = data["choices"][0]["message"]["content"].strip()
    # Strip markdown fences if present
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]
    return text.strip()

def generate_danmaku(chapter_data, book_title):
    content = chapter_data.get("content", [])
    # Build eligible paragraph list
    eligible = []
    for i, p in enumerate(content):
        txt = p.strip()
        if len(txt) >= MIN_PARAGRAPH_CHARS:
            eligible.append((i, txt[:80]))
    if not eligible:
        return []
    para_list = "\n".join(f"  ✅ [{i}] {preview}..." for i, preview in eligible)
    # Full text for context (truncated to ~4000 chars to fit context)
    full_text = "\n".join(f"[{i}] {p}" for i, p in enumerate(content))[:4000]
    count = random.randint(10, 12)
    prompt = PROMPT_TEMPLATE.format(count=count, paragraphs_list=para_list, chapter_text=full_text)
    for attempt in range(3):
        try:
            raw = call_llm(prompt)
            entries = json.loads(raw)
            if isinstance(entries, list):
                return entries
        except Exception as e:
            print(f"    LLM attempt {attempt+1} failed: {e}", file=sys.stderr)
            time.sleep(5 * (attempt + 1))
    return []

def seed_chapter(s3, book_id, ch_id, book_title):
    chapter = get_chapter(book_id, ch_id)
    if not chapter or not chapter.get("content"):
        print(f"    Ch {ch_id}: empty, skipping")
        return 0
    raw_entries = generate_danmaku(chapter, book_title)
    if not raw_entries:
        print(f"    Ch {ch_id}: LLM returned nothing, skipping")
        return 0
    now = int(time.time())
    entries = []
    for i, e in enumerate(raw_entries):
        idx = e.get("paragraph_idx", 0)
        content = str(e.get("content", ""))[:140]
        rtype = "emoji" if e.get("reaction_type") == "emoji" else "text"
        entries.append({
            "id": i + 1,
            "paragraph_idx": idx,
            "content": content,
            "reaction_type": rtype,
            "session_hash": f"seed_bot_{random.randint(1000,9999)}",
            "created_at": now - random.randint(600, 86400 * 7),
        })
    danmaku_file = {"book_id": book_id, "chapter_id": ch_id, "entries": entries}
    key = r2_key(book_id, ch_id)
    s3.put_object(Bucket="novel-data", Key=key, Body=json.dumps(danmaku_file))
    print(f"    Ch {ch_id}: ✅ seeded {len(entries)} danmaku")
    return len(entries)

def main():
    global API_BASE, API_KEY
    load_env()
    API_BASE, API_KEY, _ = get_llm_config()
    books = get_books()
    s3 = get_r2_client()
    total = 0
    for b in books:
        bid = b["id"]
        title = b["title"]
        print(f'\n📖 Book {bid}: "{title}"')
        catalog = get_catalog(bid)
        chs = catalog.get("chapters", [])[:3]
        for ch in chs:
            cid = ch["chapter_id"]
            n = seed_chapter(s3, bid, cid, title)
            total += n
            time.sleep(1)
    print(f"\n✅ Done! Total danmaku seeded: {total}")

if __name__ == "__main__":
    main()
