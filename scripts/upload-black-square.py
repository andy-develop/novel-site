#!/usr/bin/env python3
"""Phase 6B manual R2 upload for Jury of Twelve (new book, no existing highlights)."""
import json, os, re, sys, time
from pathlib import Path
import boto3, urllib.request

# --- env ---
def load_env(path):
    env = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip()
    return env

env = load_env('/root/novel-site/.env')
hemenv = load_env('/root/.hermes/.env')
R2 = boto3.client('s3', endpoint_url=env['R2_ENDPOINT'],
                  aws_access_key_id=env['R2_ACCESS_KEY_ID'],
                  aws_secret_access_key=env['R2_SECRET_ACCESS_KEY'],
                  region_name='auto')
BUCKET = env['R2_BUCKET']
API_BASE = 'https://ark.cn-beijing.volces.com/api/v3'
API_KEY = hemenv.get('HERMES_CUSTOM_ARK_CN_BEIJING_VOLCES_COM_API_KEY', '').strip('"').strip("'")
MODEL = 'deepseek-v4-flash-ga-260731'
BOOK_ID = 1330
CH_DIR = Path('/root/novels/black-square/chapters')

def r2_get(key):
    try:
        return json.loads(R2.get_object(Bucket=BUCKET, Key=key)['Body'].read())
    except Exception:
        return None

def r2_put(key, data, cc='public, max-age=31536000, immutable'):
    R2.put_object(Bucket=BUCKET, Key=key, Body=json.dumps(data, ensure_ascii=False).encode(),
                  ContentType='application/json', CacheControl=cc)
    print(f'  PUT {key} ({len(json.dumps(data, ensure_ascii=False))} bytes)')

def llm_highlight(title, content_text):
    text = content_text[:5000] + ('...' if len(content_text) > 5000 else '')
    prompt = ("You are a masterful book editor. Generate a single compelling \"chapter highlight\" line for this novel chapter.\n"
              "Rules:\n- One sentence, max 25 words\n- Must be eye-catching and hook the reader's curiosity\n"
              "- Can be a striking quote from the text OR a teasing summary of the core suspense\n"
              "- Do NOT wrap in quotes\n- Do NOT start with \"In this chapter\" or similar meta-language\n\n"
              f"Chapter title: {title}\nChapter text:\n{text}")
    body = json.dumps({'model': MODEL, 'messages': [{'role': 'user', 'content': prompt}],
                       'max_tokens': 60, 'temperature': 0.7}).encode()
    req = urllib.request.Request(f'{API_BASE}/chat/completions', data=body, headers={
        'Content-Type': 'application/json', 'Authorization': f'Bearer {API_KEY}'})
    with urllib.request.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read())
    hl = result['choices'][0]['message']['content'].strip().strip('"').strip("'")
    hl = re.sub(r'\n.*', '', hl).strip()
    return hl

def parse_chapter(text):
    lines = text.strip().split('\n')
    title = lines[0].lstrip('# ').strip() if lines and lines[0].startswith('#') else 'Chapter'
    paras = [p.strip() for p in text.split('\n\n') if p.strip() and not p.strip().startswith('#')]
    return title, paras

# --- slug collision check ---
books = r2_get('books.json') or []
slugs = {b.get('slug') for b in books}
assert 'black-square' not in slugs, f'SLUG COLLISION: black-square exists (ids {[b["id"] for b in books if b.get("slug")=="black-square"]})'
max_id = max(b['id'] for b in books)
assert BOOK_ID == max_id + 1, f'BOOK_ID {BOOK_ID} != max_id+1 ({max_id+1})'
print(f'Slug OK. max_id={max_id}, using id={BOOK_ID}')

# --- chapter files ---
files = sorted(CH_DIR.glob('ch*.md'))
chapters = []
catalog = []
hl_ok = hl_fail = 0
for f in files:
    m = re.search(r'ch(\d+)', f.name)
    ch_id = int(m.group(1))
    title, paras = parse_chapter(f.read_text(encoding='utf-8'))
    if not re.match(r'^Chapter\s+\d+', title):
        title = f'Chapter {ch_id}: {title}'
    content_text = '\n\n'.join(paras)
    highlight = ''
    for attempt in range(3):
        try:
            highlight = llm_highlight(title, content_text)
            if highlight:
                hl_ok += 1
                break
        except Exception as e:
            print(f'  ch{ch_id} LLM attempt {attempt+1} failed: {e}')
            time.sleep(3 * (attempt + 1))
    if not highlight:
        hl_fail += 1
        highlight = ''
        print(f'  ch{ch_id}: highlight FAILED')
    else:
        print(f'  ch{ch_id} hl: {highlight[:70]}')
    ch_obj = {'book_id': BOOK_ID, 'chapter_id': ch_id, 'title': title,
              'content': paras, 'highlight': highlight}
    r2_put(f'{BOOK_ID}/{ch_id}.json', ch_obj)
    catalog.append({'chapter_id': ch_id, 'title': title})
    chapters.append((ch_id, title))
    time.sleep(0.4)

# --- catalog ---
r2_put(f'catalog_{BOOK_ID}.json', {'book_id': BOOK_ID, 'chapters': catalog})

# --- books.json ---
meta = {'title': 'Black Square', 'author': 'Apex Shaw',
        'category': 'Revenge Thriller / Tech Drama / Social Media / Female Lead',
        'intro': ("Mara Chen was the internet's most feared truth-teller, until her sister Priya leaked a bitter DM and got her cancelled overnight. "
                  "A year of digital exile. One anonymous chess master. When a hacked group chat reveals Priya's perfect life is a scripted content farm, "
                  "Mara crawls back online with a 64-square plan. She does not rant. She plays. They took her voice, she learned to checkmate."),
        'lang': 'english', 'tags': ['Revenge', 'Thriller', 'Social Media', 'Female Lead', 'Comeback']}
books = [b for b in books if b['id'] != BOOK_ID]
books.append({'id': BOOK_ID, 'slug': 'black-square', 'title': meta['title'],
              'author': meta['author'], 'category': meta['category'], 'intro': meta['intro'],
              'total_chapters': len(catalog), 'lang': meta['lang'], 'tags': meta['tags']})
books.sort(key=lambda b: b['id'])
R2.put_object(Bucket=BUCKET, Key='books.json',
              Body=json.dumps(books, ensure_ascii=False, indent=2).encode(),
              ContentType='application/json',
              CacheControl='no-cache, no-store, must-revalidate')
print(f'  PUT books.json ({len(books)} books)')
print(f'DONE. Book {BOOK_ID} uploaded: {len(catalog)} chapters, highlights {hl_ok} ok / {hl_fail} fail')
