#!/usr/bin/env python3
"""Fix character epic_nodes that have <3 links.
Reads characters_{bookId}.json, fetches chapter highlights,
asks LLM to pick 3-5 key chapters per character, uploads fixed version."""

import json, os, sys, time, re, urllib.request

# ─── Config ───
R2_PUBLIC = 'https://data.lyriq.space'

def load_env():
    env = {}
    with open('/root/novel-site/.env') as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                env[k] = v
    return env

def get_s3(env):
    import boto3
    return boto3.client('s3',
        endpoint_url=env['R2_ENDPOINT'],
        aws_access_key_id=env['R2_ACCESS_KEY_ID'],
        aws_secret_access_key=env['R2_SECRET_ACCESS_KEY'],
        region_name='auto')

def r2_get(key, env):
    import boto3
    s3 = get_s3(env)
    try:
        obj = s3.get_object(Bucket=env.get('R2_BUCKET','novel-data'), Key=key)
        return json.loads(obj['Body'].read())
    except:
        pass
    url = f'{R2_PUBLIC}/{key}'
    req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f'  [WARN] Failed to fetch {key}: {e}')
        return None

def r2_put(key, data, env):
    s3 = get_s3(env)
    body = json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8')
    s3.put_object(Bucket=env.get('R2_BUCKET','novel-data'), Key=key, Body=body,
        ContentType='application/json',
        CacheControl='no-cache, no-store, must-revalidate')

def load_llm_config():
    import yaml
    with open('/root/.hermes/config.yaml') as f:
        cfg = yaml.safe_load(f)
    m = cfg.get('model', {})
    return m.get('base_url',''), m.get('api_key',''), m.get('default','')

LLM_API_BASE, LLM_API_KEY, _ = load_llm_config()

def call_llm(prompt, max_tokens=600, temperature=0.3):
    body = json.dumps({
        'model': os.environ.get('HL_MODEL', 'Qwen/Qwen3-32B'),
        'messages': [{'role':'user','content':prompt}],
        'max_tokens': max_tokens,
        'temperature': temperature
    }).encode()
    req = urllib.request.Request(
        f'{LLM_API_BASE}/chat/completions',
        data=body,
        headers={'Content-Type':'application/json','Authorization':f'Bearer {LLM_API_KEY}'})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                result = json.loads(resp.read())
            return result['choices'][0]['message']['content'].strip()
        except Exception as e:
            print(f'  [LLM attempt {attempt+1} failed: {e}]')
            if attempt < 2: time.sleep(5*(attempt+1))
    return None

def get_all_highlights(book_id, catalog, env):
    """Get all chapter highlights for a book - batch fetch via threading."""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    highlights = {}
    chapters = catalog.get('chapters', [])

    def fetch_one(ch):
        ch_id = ch['chapter_id']
        ch_title = ch.get('title', f'Ch.{ch_id}')
        ch_data = r2_get(f'{book_id}/{ch_id}.json', env)
        hl = ch_data.get('highlight', '') if ch_data else ''
        return ch_id, {'title': ch_title, 'highlight': hl}

    with ThreadPoolExecutor(max_workers=8) as ex:
        futures = {ex.submit(fetch_one, ch): ch for ch in chapters}
        for f in as_completed(futures):
            try:
                ch_id, data = f.result()
                highlights[ch_id] = data
            except:
                pass
    return highlights

def fix_book_characters(book_id, env, dry_run=False):
    """Fix characters with <3 epic_nodes for a single book."""
    # Load character data
    cdata = r2_get(f'characters_{book_id}.json', env)
    if not cdata:
        print(f'  No character file found')
        return False

    # Load catalog
    catalog = r2_get(f'catalog_{book_id}.json', env)
    if not catalog:
        print(f'  No catalog found')
        return False

    # Find weak characters ( <3 nodes)
    weak = {}
    for cid, cd in cdata.items():
        nodes = cd.get('dossier', {}).get('epic_nodes', [])
        if len(nodes) < 3:
            weak[cid] = cd

    if not weak:
        print(f'  All characters have 3+ links, skipping')
        return True

    print(f'  {len(weak)} characters need more links')

    # Get highlights
    hls = get_all_highlights(book_id, catalog, env)
    hl_text = '\n'.join(
        f"Ch{cid}: {d['title']} | {d['highlight'] or '(none)'}"
        for cid, d in sorted(hls.items())
    )

    # Build prompt for LLM - list weak characters and ask to pick chapters
    char_list = []
    for cid, cd in weak.items():
        name = cd.get('primary_name', cid)
        aliases = cd.get('aliases', [name])
        existing_urls = [n['url'] for n in cd.get('dossier', {}).get('epic_nodes', [])]
        existing_chs = []
        for u in existing_urls:
            m = re.search(r'/(\d+)$', u)
            if m:
                existing_chs.append(int(m.group(1)))
        char_list.append({
            'id': cid, 'name': name,
            'aliases': aliases[:5],
            'existing_chapters': existing_chs
        })

    prompt = f"""For each character below, pick 3-5 key chapter numbers (from the highlights list) where they have pivotal moments.
Rules:
- Pick chapters where this character is central (first appearance, emotional climax, betrayal, reunion, etc.)
- Do NOT repeat existing chapters already assigned
- Prefer chapters with highlights that mention the character or their storyline
- Return ONLY valid JSON: {{"char_id": [chapter_nums]}}

All chapter highlights:
{hl_text}

Characters needing chapter assignments:
"""
    for c in char_list:
        prompt += f'\n- id="{c["id"]}" name="{c["name"]}" aliases={c["aliases"]} existing_chapters={c["existing_chapters"]}'

    prompt += '\n\nReturn JSON:'

    # Call LLM
    llm_out = call_llm(prompt, max_tokens=400, temperature=0.3)
    if not llm_out:
        print(f'  LLM returned nothing, skipping')
        return False

    # Parse LLM output
    llm_out = re.sub(r'^```(?:json)?\s*', '', llm_out.strip())
    llm_out = re.sub(r'\s*```\s*$', '', llm_out)
    llm_out = re.sub(r'<think>.*?</think>', '', llm_out, flags=re.DOTALL)
    try:
        parsed = json.loads(llm_out)
    except json.JSONDecodeError:
        m = re.search(r'\{[\s\S]*\}', llm_out)
        if m:
            try:
                parsed = json.loads(m.group())
            except:
                print(f'  Could not parse LLM output, skipping')
                return False
        else:
            print(f'  No JSON in LLM output, skipping')
            return False

    # Apply: merge new chapters into existing epic_nodes
    ch_titles = {ch['chapter_id']: ch.get('title', f'Ch.{ch["chapter_id"]}')
                 for ch in catalog.get('chapters', [])}

    for c in char_list:
        cid = c['id']
        new_chs = parsed.get(cid, parsed.get(c['name'], []))
        if not isinstance(new_chs, list):
            continue

        existing_nodes = cdata[cid].get('dossier', {}).get('epic_nodes', [])
        existing_ch_set = set()
        for n in existing_nodes:
            m = re.search(r'/(\d+)$', n['url'])
            if m:
                existing_ch_set.add(int(m.group(1)))

        for ch_num in new_chs:
            ch_num = int(ch_num)
            if ch_num in existing_ch_set:
                continue
            if ch_num not in ch_titles:
                continue
            title = ch_titles[ch_num]
            short = re.sub(r'^Chapter\s+\d+:\s*', '', title)[:50] or f'Ch.{ch_num}'
            existing_nodes.append({
                'title': f'📖 {short}',
                'url': f'/novel/{book_id}/{ch_num}'
            })
            existing_ch_set.add(ch_num)

        cdata[cid]['dossier']['epic_nodes'] = existing_nodes
        print(f'  {c["name"]}: now {len(existing_nodes)} links')

    # Content-search fallback: for characters still <3 links, search chapter text
    still_weak = {cid: cd for cid, cd in cdata.items()
                  if len(cd.get('dossier', {}).get('epic_nodes', [])) < 3}
    if still_weak:
        ch_ids = [ch['chapter_id'] for ch in catalog.get('chapters', [])]
        ch_titles = {ch['chapter_id']: ch.get('title', f'Ch.{ch["chapter_id"]}')
                     for ch in catalog.get('chapters', [])}
        for cid, cd in still_weak.items():
            nodes = cd.get('dossier', {}).get('epic_nodes', [])
            need = 3 - len(nodes)
            existing_ch_set = set()
            for n in nodes:
                m = re.search(r'/(\d+)$', n['url'])
                if m: existing_ch_set.add(int(m.group(1)))
            # Search by primary_name and aliases
            search_terms = [cd.get('primary_name', '')] + cd.get('aliases', [])[:3]
            search_terms = [t for t in search_terms if t and len(t) >= 3]
            if not search_terms:
                continue
            found = []
            for ch_id in ch_ids:
                if ch_id in existing_ch_set:
                    continue
                ch_data = r2_get(f'{book_id}/{ch_id}.json', env)
                if not ch_data:
                    continue
                content = str(ch_data.get('content', '')) + ' ' + str(ch_data.get('highlight', ''))
                for term in search_terms:
                    if term in content:
                        found.append(ch_id)
                        break
                if len(found) >= need:
                    break
            for ch_num in found:
                title = ch_titles.get(ch_num, f'Ch.{ch_num}')
                short = re.sub(r'^Chapter\s+\d+:\s*', '', title)[:50] or f'Ch.{ch_num}'
                nodes.append({'title': f'📖 {short}', 'url': f'/novel/{book_id}/{ch_num}'})
            if found:
                cdata[cid]['dossier']['epic_nodes'] = nodes
                print(f'  {cd.get("primary_name", cid)}: content-search +{len(found)} → {len(nodes)} links')

    # Upload
    if not dry_run:
        r2_put(f'characters_{book_id}.json', cdata, env)
        print(f'  Uploaded characters_{book_id}.json')
    else:
        print(f'  [DRY RUN] would upload')
    return True

def create_book_characters(book_id, env, dry_run=False):
    """Create characters file for books that don't have one (Chinese books etc)."""
    import yaml
    catalog = r2_get(f'catalog_{book_id}.json', env)
    if not catalog:
        print(f'  No catalog found')
        return False

    # Get book info
    books = r2_get('books.json', env)
    book_info = next((b for b in books if b['id'] == book_id), None)
    book_title = book_info.get('title', f'Book {book_id}') if book_info else f'Book {book_id}'

    # Sample first 5 chapters + all highlights
    ch_info = []
    for ch in catalog.get('chapters', [])[:5]:
        ch_id = ch['chapter_id']
        ch_data = r2_get(f'{book_id}/{ch_id}.json', env)
        content = ''
        hl = ''
        if ch_data:
            hl = ch_data.get('highlight', '')
            content = '\n'.join(ch_data.get('content', []))[:2000]
        ch_info.append(f"--- Chapter {ch_id}: {ch.get('title','')} ---\nHighlight: {hl}\n{content}")

    sample_text = '\n\n'.join(ch_info)

    all_hl = []
    for ch in catalog.get('chapters', []):
        ch_id = ch['chapter_id']
        ch_data = r2_get(f'{book_id}/{ch_id}.json', env)
        hl = ch_data.get('highlight', '') if ch_data else ''
        all_hl.append({'id': ch_id, 'title': ch.get('title',''), 'hl': hl})

    hl_text = '\n'.join(f"Ch{c['id']}: {c['hl'] or '(none)'}" for c in all_hl)
    ch_titles = {ch['chapter_id']: ch.get('title', '') for ch in catalog.get('chapters', [])}

    lang = book_info.get('lang', 'en') if book_info else 'en'
    lang_note = "Use Chinese for all names, aliases, and descriptions." if lang in ('chinese', 'zh') else "Use English."

    prompt = f"""Analyze this novel "{book_title}" and extract the core characters.

{lang_note}

Sample chapters:
{sample_text}

All chapter highlights:
{hl_text}

Return ONLY valid JSON (no markdown, no code fences):
{{
  "characters": [
    {{
      "id": "lowercase_underscore_id",
      "name": "Full Name",
      "aliases": ["Name", "Alias1", "Alias2"],
      "epic_chapters": [1, 5, 12]
    }}
  ]
}}

Rules:
- Include only 2-3 most important characters (POV characters, love interests, antagonists)
- Quality over quantity — only characters who appear in 3+ chapters
- epic_chapters: pick 3-5 chapters where this character has a pivotal moment
  (first appearance, emotional climax, betrayal, reunion, etc.)
- Use chapter numbers from the highlights list"""

    print(f'  Calling LLM for character extraction...')
    llm_out = call_llm(prompt, max_tokens=800)
    if not llm_out:
        print(f'  LLM returned nothing')
        return False

    llm_out = re.sub(r'^```(?:json)?\s*', '', llm_out.strip())
    llm_out = re.sub(r'\s*```\s*$', '', llm_out)
    llm_out = re.sub(r'🤔.*?✅', '', llm_out, flags=re.DOTALL)
    try:
        parsed = json.loads(llm_out)
    except json.JSONDecodeError:
        m = re.search(r'\{[\s\S]*\}', llm_out)
        if m:
            try:
                parsed = json.loads(m.group())
            except:
                print(f'  Could not parse LLM output')
                return False
        else:
            return False

    char_list = parsed.get('characters', [])
    if not char_list:
        print(f'  No characters in output')
        return False

    result = {}
    for c in char_list:
        cid = c.get('id', c['name'].lower().replace(' ', '_'))
        aliases = [c['name']] + [a for a in c.get('aliases', []) if a != c['name']]
        epic_chs = c.get('epic_chapters', [])[:5]
        epic_nodes = []
        for ch_num in epic_chs:
            title = ch_titles.get(ch_num, f'Ch.{ch_num}')
            short = re.sub(r'^Chapter\s+\d+:\s*', '', title)[:50] or f'Ch.{ch_num}'
            epic_nodes.append({'title': f'📖 {short}', 'url': f'/novel/{book_id}/{ch_num}'})
        result[cid] = {
            'primary_name': c['name'],
            'aliases': aliases,
            'dossier': {'title': c['name'], 'epic_nodes': epic_nodes}
        }

    print(f'  Generated {len(result)} characters')
    if not dry_run:
        r2_put(f'characters_{book_id}.json', result, env)
        print(f'  Uploaded characters_{book_id}.json')
    else:
        print(f'  [DRY RUN]')
    return True

def main():
    env = load_env()
    dry_run = '--dry-run' in sys.argv
    mode = 'all'  # default: fix links for all books with weak chars

    # Parse args
    target_books = None
    create_mode = False
    for arg in sys.argv[1:]:
        if arg.startswith('--book='):
            target_books = [int(x) for x in arg.split('=')[1].split(',')]
        if arg == '--create':
            create_mode = True

    if create_mode:
        # Create missing character files
        missing_ids = [1, 2, 3, 4, 5, 21, 23]
        if target_books:
            missing_ids = target_books
        for bid in missing_ids:
            print(f'\n📚 Book {bid}: Creating characters file')
            try:
                create_book_characters(bid, env, dry_run)
            except Exception as e:
                print(f'  [ERROR] {e}')
            time.sleep(1)
    else:
        # Fix weak links
        books = r2_get('books.json', env)
        if not books:
            print('ERROR: Cannot fetch books.json')
            sys.exit(1)

        for b in books:
            bid = b['id']
            if target_books and bid not in target_books:
                continue
            # Check if char file exists and has weak chars
            try:
                cdata = r2_get(f'characters_{bid}.json', env)
                if not cdata:
                    continue
                has_weak = any(
                    len(cd.get('dossier', {}).get('epic_nodes', [])) < 3
                    for cd in cdata.values()
                )
                if not has_weak:
                    continue
            except:
                continue

            print(f'\n📚 Book {bid}: {b.get("title","")}')
            try:
                fix_book_characters(bid, env, dry_run)
            except Exception as e:
                print(f'  [ERROR] {e}')
            time.sleep(1)

    print('\nDone!')

if __name__ == '__main__':
    main()
