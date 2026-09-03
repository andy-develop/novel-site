#!/usr/bin/env python3
"""Manual R2 upload for lyriq.space novel (Phase 6B — preserves/maps old highlights,
generates new ones via LLM). Usage: python3 upload_novel_r2.py --id N --dir <slug>"""
import json, os, re, sys, argparse, time, urllib.request
from pathlib import Path
import boto3

ENV_FILE = Path("/root/novel-site/.env")
HERMES_ENV = Path("/root/.hermes/.env")

def load_env(path):
    env = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        k, v = k.strip(), v.strip()
        if k.isidentifier():
            env[k] = v
    return env

def parse_chapter(path):
    """H1 first line -> title; non-# paragraphs -> content."""
    text = path.read_text(encoding='utf-8')
    lines = text.split('\n')
    title = ''
    for ln in lines:
        if ln.startswith('#'):
            title = ln.lstrip('#').strip()
            break
    paras = [p.strip() for p in text.split('\n\n') if p.strip() and not p.strip().startswith('#')]
    return title, paras

def llm_highlight(title, first_para, api_base, model, api_key):
    prompt = (f"Write ONE sentence chapter highlight (max 25 words) for this web-novel chapter. "
              f"No quotes, no meta-language, punchy, spoiler-free tease. Chapter title: {title}. "
              f"Opening: {first_para[:200]}")
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 60,
        "temperature": 0.7,
    }).encode()
    req = urllib.request.Request(api_base.rstrip('/') + "/chat/completions", data=body,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"})
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            data = json.loads(r.read().decode())
            return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"  [highlight LLM error: {e}]", file=sys.stderr)
        return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--id', type=int, required=True)
    ap.add_argument('--dir', required=True)
    ap.add_argument('--skip-highlights', action='store_true', help='Skip LLM calls (use fallback)')
    args = ap.parse_args()

    env = load_env(ENV_FILE)
    hermes_env = load_env(HERMES_ENV)
    bucket = env['R2_BUCKET']
    s3 = boto3.client('s3', endpoint_url=env['R2_ENDPOINT'],
                      aws_access_key_id=env['R2_ACCESS_KEY_ID'],
                      aws_secret_access_key=env['R2_SECRET_ACCESS_KEY'], region_name='auto')

    book_id = args.id
    proj_dir = Path('/root/novels') / args.dir
    ch_dir = proj_dir / 'chapters'
    ch_files = sorted(ch_dir.glob('ch*.md'), key=lambda p: int(re.search(r'(\d+)', p.name).group(1)))
    print(f"Found {len(ch_files)} chapters in {ch_dir}")

    # Load project yaml
    import yaml
    data = yaml.safe_load((proj_dir / 'novel-project.yaml').read_text()) or {}
    meta = data.get('meta', data)
    title = meta.get('title', args.dir)
    author = meta.get('author', 'Apex Shaw')
    genre = meta.get('genre', '')
    lang = (meta.get('language') or 'english').lower()
    intro = ''
    for field in ['premise', 'pitch', 'logline', 'core_conflict', 'tagline']:
        if meta.get(field):
            intro = str(meta[field])[:200]
            break

    # Tag mapping (same as upload-script)
    SYN = {"Fantasy": ["fantasy","dark fantasy","urban fantasy","werewolf","litrpg","eldritch","vampire","cozy fantasy","gothic"],
           "Romance": ["romance","monster romance","stalker romance","dark romance","sweet pet","harem","love triangle","enemies-to-lovers","exes-to-lovers","lovers"],
           "Sci-Fi": ["sci-fi","scifi","science fiction","cyberpunk","cyber","tech thriller","tech-thriller"],
           "Thriller": ["thriller","political thriller","tech thriller","cyber thriller","psychological thriller","psychological horror","horror","mystery","suspense","gaslighting","booktok"],
           "Dystopia": ["dystopia","dystopian","post-apocalyptic","apocalyptic"],
           "Dark Academia": ["dark academia"], "Contemporary": ["contemporary","satire","dark comedy"],
           "Queer": ["sapphic","queer","lgbtq","gender fluid"],
           "Female Lead": ["female lead","female protagonist","female empowerment","feminism","feminist"]}
    gtext = (genre or '').lower().replace('-', ' ')
    tags = sorted({t for t, kws in SYN.items() if any(k in gtext for k in kws)})

    # Load existing books.json, find slug
    books = json.loads(s3.get_object(Bucket=bucket, Key='books.json')['Body'].read())
    existing = {b['id']: b for b in books}
    if book_id in existing:
        print(f"WARNING: id {book_id} exists: {existing[book_id].get('title')}")
    slug = args.dir
    # find existing entry for slug (for highlight mapping)
    old_books_entry = next((b for b in books if b.get('slug') == slug), None)

    # Fetch old chapters for highlight mapping
    old_highlights = {}  # prefix80 -> highlight
    if old_books_entry:
        old_id = old_books_entry['id']
        for n in range(1, 200):
            try:
                obj = s3.get_object(Bucket=bucket, Key=f'{old_id}/{n}.json')
                ch = json.loads(obj['Body'].read())
                if ch.get('content') and ch.get('highlight'):
                    old_highlights[ch['content'][0][:80]] = ch['highlight']
            except Exception:
                break
        print(f"Mapped {len(old_highlights)} old highlights from book id {old_id}")

    # LLM config
    api_key = (hermes_env.get('HERMES_CUSTOM_ARK_CN_BEIJING_VOLCES_COM_API_KEY') or '').strip('"\'')
    api_base = "https://ark.cn-beijing.volces.com/api/v3"
    model = "deepseek-v4-flash-ga-260731"

    chapters = []
    for f in ch_files:
        n = int(re.search(r'(\d+)', f.name).group(1))
        t, paras = parse_chapter(f)
        if not t:
            t = f"Chapter {n}"
        highlight = None
        if paras and not args.skip_highlights:
            key = paras[0][:80]
            if key in old_highlights:
                highlight = old_highlights[key]
                print(f"  ch{n}: mapped old highlight")
            else:
                hl = llm_highlight(t, paras[0], api_base, model, api_key)
                if hl:
                    hl = hl.strip().strip('"').strip("'")
                    if len(hl) > 160:
                        hl = hl[:157] + '...'
                    highlight = hl
                    print(f"  ch{n}: new highlight: {hl[:60]}")
        if not highlight:
            highlight = (paras[0][:120] + '...') if paras else 'A chapter of SHE WOKE UP.'
        chapters.append({"book_id": book_id, "chapter_id": n, "title": t, "content": paras, "highlight": highlight})

    # PUT chapter objects
    for ch in chapters:
        body = json.dumps(ch, ensure_ascii=False).encode()
        s3.put_object(Bucket=bucket, Key=f'{book_id}/{ch["chapter_id"]}.json', Body=body,
                      ContentType='application/json', CacheControl='public, max-age=31536000, immutable')
    print(f"Uploaded {len(chapters)} chapter objects")

    # PUT catalog
    catalog = {"book_id": book_id, "title": title, "author": author, "genre": genre,
               "tags": tags, "language": lang, "intro": intro, "total_chapters": len(chapters),
               "chapters": [{"id": c["chapter_id"], "title": c["title"]} for c in chapters]}
    s3.put_object(Bucket=bucket, Key=f'catalog_{book_id}.json', Body=json.dumps(catalog, ensure_ascii=False).encode(),
                  ContentType='application/json', CacheControl='public, max-age=31536000, immutable')

    # Update books.json
    entry = {"id": book_id, "slug": slug, "title": title, "author": author, "genre": genre,
             "lang": lang, "tags": tags, "intro": intro, "total_chapters": len(chapters)}
    new_books = [b for b in books if b.get('slug') != slug and b['id'] != book_id]
    new_books.append(entry)
    new_books.sort(key=lambda b: b['id'])
    s3.put_object(Bucket=bucket, Key='books.json', Body=json.dumps(new_books, ensure_ascii=False).encode(),
                  ContentType='application/json', CacheControl='no-cache, no-store, must-revalidate')
    print(f"books.json updated: id={book_id} slug={slug} total_chapters={len(chapters)} lang={lang}")
    print("DONE")

if __name__ == '__main__':
    main()
