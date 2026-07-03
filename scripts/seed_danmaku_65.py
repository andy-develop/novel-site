#!/usr/bin/env python3
"""Cold-start danmaku seeder for book 65 only — uses boto3 for R2 reads/writes."""

import json, sys, os, time, random
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SCRIPT_DIR))

BOOK_ID = 65
BOOK_TITLE = "The Rules of the Rabbit Hole"

# ---- Config ----
DANMAKU_PER_CHAPTER = 11
MIN_PARAGRAPH_CHARS = 120
MODEL = os.environ.get("HL_MODEL", "Qwen/Qwen3-32B")
TIMEOUT = 180


def get_llm_config():
    import yaml
    with open("/root/.hermes/config.yaml") as f:
        cfg = yaml.safe_load(f)
    m = cfg.get("model", {})
    return m.get("base_url", ""), m.get("api_key", ""), m.get("default", "")


def load_env():
    env_file = SCRIPT_DIR / ".env"
    env = {}
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def get_r2_client(env):
    import boto3
    return boto3.client(
        "s3",
        endpoint_url=env["R2_ENDPOINT"],
        aws_access_key_id=env["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=env["R2_SECRET_ACCESS_KEY"],
        region_name="auto",
    )


def r2_get(s3, bucket, key):
    obj = s3.get_object(Bucket=bucket, Key=key)
    return json.loads(obj["Body"].read())


def r2_put(s3, bucket, key, data):
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(data, ensure_ascii=False).encode("utf-8"),
        ContentType="application/json",
        CacheControl="no-cache, no-store, must-revalidate",
    )


def r2_key(ch_id):
    return f"danmaku/{BOOK_ID}/{ch_id}.json"


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


def call_llm(prompt, api_base, api_key):
    import urllib.request
    body = json.dumps(
        {
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.9,
            "max_tokens": 2000,
        }
    ).encode()
    req = urllib.request.Request(
        f"{api_base}/chat/completions",
        data=body,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        data = json.loads(resp.read())
    text = data["choices"][0]["message"]["content"].strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]
    return text.strip()


def generate_danmaku(chapter_data, book_title, api_base, api_key):
    content = chapter_data.get("content", [])
    eligible = []
    for i, p in enumerate(content):
        txt = p.strip()
        if len(txt) >= MIN_PARAGRAPH_CHARS:
            eligible.append((i, txt[:80]))
    if not eligible:
        print(f"    No eligible paragraphs")
        return []
    para_list = "\n".join(f"  ✅ [{i}] {preview}..." for i, preview in eligible)
    full_text = "\n".join(f"[{i}] {p}" for i, p in enumerate(content))[:4000]
    count = random.randint(10, 12)
    prompt = PROMPT_TEMPLATE.format(count=count, paragraphs_list=para_list, chapter_text=full_text)
    for attempt in range(3):
        try:
            raw = call_llm(prompt, api_base, api_key)
            entries = json.loads(raw)
            if isinstance(entries, list):
                return entries
        except Exception as e:
            print(f"    LLM attempt {attempt+1} failed: {e}", file=sys.stderr)
            time.sleep(5 * (attempt + 1))
    return []


def seed_chapter(s3, bucket, ch_id, api_base, api_key):
    chapter = r2_get(s3, bucket, f"{BOOK_ID}/{ch_id}.json")
    if not chapter or not chapter.get("content"):
        print(f"    Ch {ch_id}: empty, skipping")
        return 0
    raw_entries = generate_danmaku(chapter, BOOK_TITLE, api_base, api_key)
    if not raw_entries:
        print(f"    Ch {ch_id}: LLM returned nothing, skipping")
        return 0
    now = int(time.time())
    entries = []
    for i, e in enumerate(raw_entries):
        idx = e.get("paragraph_idx", 0)
        content = str(e.get("content", ""))[:140]
        rtype = "emoji" if e.get("reaction_type") == "emoji" else "text"
        entries.append(
            {
                "id": i + 1,
                "paragraph_idx": idx,
                "content": content,
                "reaction_type": rtype,
                "session_hash": f"seed_bot_{random.randint(1000, 9999)}",
                "created_at": now - random.randint(600, 86400 * 7),
            }
        )
    danmaku_file = {"book_id": BOOK_ID, "chapter_id": ch_id, "entries": entries}
    r2_put(s3, bucket, r2_key(ch_id), danmaku_file)
    print(f"    Ch {ch_id}: ✅ seeded {len(entries)} danmaku")
    return len(entries)


def main():
    env = load_env()
    api_base, api_key, _ = get_llm_config()
    s3 = get_r2_client(env)
    bucket = env.get("R2_BUCKET", "novel-data")

    catalog = r2_get(s3, bucket, f"catalog_{BOOK_ID}.json")
    chs = catalog.get("chapters", [])[:3]
    total = 0
    print(f'\n📖 Book {BOOK_ID}: "{BOOK_TITLE}"')
    for ch in chs:
        cid = ch["chapter_id"]
        n = seed_chapter(s3, bucket, cid, api_base, api_key)
        total += n
        time.sleep(1)
    print(f"\n✅ Done! Total danmaku seeded: {total}")


if __name__ == "__main__":
    main()
