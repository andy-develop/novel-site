#!/usr/bin/env python3
"""
Generate chapter highlights for all novels on R2.
Reads chapter content -> calls LLM -> writes highlight back to chapter JSON.
"""

import json, os, sys, time, re
import urllib.request, urllib.error

# --- R2 Config ---
def load_env():
    env = {}
    with open('/root/novel-site/.env') as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                env[k] = v
    return env

R2_PUBLIC = 'https://data.lyriq.space'

def r2_get(key):
    """Fetch object from R2 — try boto3 first, then HTTP CDN fallback."""
    # Try boto3 first (no User-Agent issue)
    try:
        import boto3
        env = load_env()
        s3 = boto3.client('s3',
            endpoint_url=env['R2_ENDPOINT'],
            aws_access_key_id=env['R2_ACCESS_KEY_ID'],
            aws_secret_access_key=env['R2_SECRET_ACCESS_KEY'],
            region_name='auto')
        obj = s3.get_object(Bucket=env.get('R2_BUCKET', 'novel-data'), Key=key)
        return json.loads(obj['Body'].read())
    except Exception:
        pass
    # HTTP fallback
    url = f'{R2_PUBLIC}/{key}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)'})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f'  [WARN] Failed to fetch {key}: {e}')
        return None

def r2_put(key, data, env):
    """Upload object to R2 via S3 API (boto3)."""
    import boto3
    s3 = boto3.client('s3',
        endpoint_url=env['R2_ENDPOINT'],
        aws_access_key_id=env['R2_ACCESS_KEY_ID'],
        aws_secret_access_key=env['R2_SECRET_ACCESS_KEY'],
        region_name='auto')
    body = json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8')
    s3.put_object(
        Bucket=env.get('R2_BUCKET', 'novel-data'),
        Key=key,
        Body=body,
        ContentType='application/json',
        CacheControl='no-cache, no-store, must-revalidate'
    )

# --- LLM Config (read from hermes config.yaml) ---
def get_llm_config():
    import yaml
    with open('/root/.hermes/config.yaml') as f:
        cfg = yaml.safe_load(f)
    m = cfg.get('model', {})
    return m.get('base_url', ''), m.get('api_key', ''), m.get('default', '')

LLM_API_BASE, LLM_API_KEY, LLM_MODEL_DEFAULT = get_llm_config()
LLM_MODEL = os.environ.get('HL_MODEL', 'Qwen/Qwen3-32B')

def generate_highlight(title, content_text, lang='en'):
    """Call LLM to generate a one-line chapter highlight."""
    # Truncate content to ~5000 chars for better quality with larger models
    text = content_text[:5000]
    if len(content_text) > 5000:
        text += '...'
    
    if lang == 'zh' or any('\u4e00' <= c <= '\u9fff' for c in title):
        prompt = f"""你是小说精读编辑。请为以下章节生成一句"本章金句"或"核心悬念"。

要求：
- 一句话，不超过40个中文字
- 要抓眼球、勾起阅读欲望
- 可以是原文中的精彩句子，也可以是你提炼的悬念摘要
- 不要用引号包裹

章节标题：{title}
章节正文：
{text}"""
    else:
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

    body = json.dumps({
        'model': LLM_MODEL,
        'messages': [{'role': 'user', 'content': prompt}],
        'max_tokens': 60,
        'temperature': 0.7
    }).encode()

    req = urllib.request.Request(
        f'{LLM_API_BASE}/chat/completions',
        data=body,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {LLM_API_KEY}',
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            result = json.loads(resp.read())
        highlight = result['choices'][0]['message']['content'].strip().strip('"').strip("'")
        # Strip LLM-generated meta prefixes (本章金句, 核心悬念, etc.)
        import re as _re
        highlight = _re.sub(r'^(?:本章金句|核心悬念)[：:]?\s*', '', highlight).strip()
        # Strip trailing meta-commentary in Chinese brackets
        highlight = _re.sub(r'\n*（[^）]*(?:解析|提炼|凝练|说明|备注|注)[^）]*）$', '', highlight, flags=_re.DOTALL).strip()
        return highlight
    except Exception as e:
        print(f'  [LLM ERROR] {e}')
        return None

# --- Main ---
def main():
    env = load_env()

    # Parse args
    target_book = None  # or list of ints when --book=1,2,3
    target_chapter = None
    dry_run = False
    start_book = None
    for arg in sys.argv[1:]:
        if arg == '--dry-run':
            dry_run = True
        elif arg.startswith('--book='):
            target_book = [int(x) for x in arg.split('=')[1].split(',')]
        elif arg.startswith('--chapter='):
            target_chapter = int(arg.split('=')[1])
        elif arg.startswith('--start-book='):
            start_book = int(arg.split('=')[1])
        elif arg.startswith('--model='):
            global LLM_MODEL
            LLM_MODEL = arg.split('=')[1]

    print(f'Using model: {LLM_MODEL}')

    # Get books list
    books = r2_get('books.json')
    if not books:
        print('ERROR: Cannot fetch books.json')
        sys.exit(1)

    total_done = 0
    total_skip = 0
    total_fail = 0

    for book in books:
        book_id = book['id']
        if target_book and book_id not in target_book:
            continue
        if start_book and book_id < start_book:
            continue

        lang = book.get('lang', '')
        lang_code = 'zh' if lang not in ('english', 'en') else 'en'
        total_ch = book.get('total_chapters', 0)
        print(f'\n📚 Book {book_id}: {book["title"]} ({total_ch} chapters, {lang_code})')

        # Get catalog
        catalog = r2_get(f'catalog_{book_id}.json')
        if not catalog:
            print(f'  [SKIP] No catalog')
            continue

        chapters = catalog.get('chapters', [])
        for ch_meta in chapters:
            ch_id = ch_meta['chapter_id']
            if target_chapter and ch_id != target_chapter:
                continue

            # Fetch chapter data
            ch_data = r2_get(f'{book_id}/{ch_id}.json')
            if not ch_data:
                print(f'  Ch {ch_id}: [SKIP] cannot fetch')
                total_skip += 1
                continue

            # Skip if already has highlight
            if ch_data.get('highlight'):
                print(f'  Ch {ch_id}: [SKIP] already has highlight')
                total_skip += 1
                continue

            # Build content text
            content_parts = ch_data.get('content', [])
            content_text = '\n\n'.join(content_parts)
            if len(content_text.strip()) < 50:
                print(f'  Ch {ch_id}: [SKIP] too short')
                total_skip += 1
                continue

            ch_title = ch_data.get('title', ch_meta.get('title', ''))

            # Generate highlight (with retry + exponential backoff)
            ch_title = ch_data.get('title', ch_meta.get('title', ''))
            highlight = None
            backoff = 5
            for attempt in range(3):
                print(f'  Ch {ch_id}: generating highlight...', end=' ', flush=True)
                highlight = generate_highlight(ch_title, content_text, lang_code)
                if highlight:
                    break
                if attempt < 2:
                    print(f'RETRY ({attempt+1}/2, wait {backoff}s)', end=' ', flush=True)
                    time.sleep(backoff)
                    backoff *= 2

            if not highlight:
                print('FAILED after 3 attempts')
                total_fail += 1
                continue

            print(f'✅ {highlight[:60]}...')
            ch_data['highlight'] = highlight
            total_done += 1

            # Upload back to R2
            if not dry_run:
                try:
                    r2_put(f'{book_id}/{ch_id}.json', ch_data, env)
                except Exception as e:
                    print(f'    [UPLOAD ERROR] {e}')
                    total_fail += 1
                    total_done -= 1
            else:
                print(f'    [DRY RUN] would upload highlight')

            # Rate limit: small delay
            time.sleep(0.5)

    print(f'\n{"="*50}')
    print(f'Done! Generated: {total_done}, Skipped: {total_skip}, Failed: {total_fail}')

if __name__ == '__main__':
    main()
