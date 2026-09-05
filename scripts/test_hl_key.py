#!/usr/bin/env python3
"""Test the highlight LLM endpoint + key before upload."""
import json, os, urllib.request

def load_env(path):
    env = {}
    for line in open(path, encoding='utf-8'):
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        env[k] = v.strip().strip('"').strip("'")
    return env

henv = load_env("/root/.hermes/.env")
key = henv.get("HERMES_CUSTOM_ARK_CN_BEIJING_VOLCES_COM_API_KEY")
print("key found:", bool(key), "len:", len(key) if key else 0)
if not key:
    raise SystemExit("NO KEY")

body = json.dumps({
    "model": "deepseek-v4-flash-ga-260731",
    "messages": [
        {"role": "system", "content": "You write one-line teaser highlights for web novel chapters. Rules: English, one sentence, under 25 words, present tense, tease the chapter's emotional peak, no quotes, no em dashes, no meta-language like 'in this chapter', no character names unless essential. Output ONLY the highlight sentence."},
        {"role": "user", "content": "Chapter title: The Villa Opens\n\nChapter text (first 1400 chars):\nPippa steps off the bus with one suitcase and a deed. The town smells like salt and regret. On the pier, a car tips over the rail with a girl inside. Pippa lifts it one-handed. The town goes silent.\n\nHighlight:"},
    ],
    "max_tokens": 60,
    "temperature": 0.7,
})
req = urllib.request.Request(
    "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
    data=body.encode(),
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"})
try:
    with urllib.request.urlopen(req, timeout=60) as r:
        out = json.loads(r.read().decode())
    print("RESPONSE:", out["choices"][0]["message"]["content"].strip())
except urllib.error.HTTPError as e:
    print("HTTP ERROR:", e.code, e.read().decode()[:500])
except Exception as e:
    print("ERROR:", e)
