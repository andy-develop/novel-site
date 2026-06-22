#!/usr/bin/env python3
"""
Generate characters_{bookId}.json for all English novels on R2.

Phase 1 (structured data): Parse characters.yaml, emotional-debts.yaml,
  threads.yaml, arc-tracker.yaml, outlines/*.md from /root/novels/{slug}/
Phase 2 (LLM fallback): For books without structured data, call LLM to
  extract character names/aliases from chapter content, and pick epic
  moments from highlights.

Output: characters_{bookId}.json uploaded to R2 per book.
"""

import json, os, sys, time, re, glob
import urllib.request, urllib.error
import yaml

# ─── Config ───

R2_PUBLIC = 'https://data.lyriq.space'
NOVELS_DIR = '/root/novels'

_env_cache = None
def load_env():
    global _env_cache
    if _env_cache is not None:
        return _env_cache
    env = {}
    with open('/root/novel-site/.env') as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                env[k] = v
    _env_cache = env
    return env

# ─── R2 I/O ───

_s3_client = None
def _get_s3_client():
    global _s3_client
    if _s3_client is None:
        import boto3
        env = load_env()
        _s3_client = boto3.client('s3',
            endpoint_url=env['R2_ENDPOINT'],
            aws_access_key_id=env['R2_ACCESS_KEY_ID'],
            aws_secret_access_key=env['R2_SECRET_ACCESS_KEY'],
            region_name='auto')
    return _s3_client

def r2_get(key):
    try:
        s3 = _get_s3_client()
        env = load_env()
        obj = s3.get_object(Bucket=env.get('R2_BUCKET', 'novel-data'), Key=key)
        return json.loads(obj['Body'].read())
    except Exception:
        pass
    url = f'{R2_PUBLIC}/{key}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f'  [WARN] Failed to fetch {key}: {e}')
        return None

def r2_put(key, data, env):
    import boto3
    s3 = boto3.client('s3',
        endpoint_url=env['R2_ENDPOINT'],
        aws_access_key_id=env['R2_ACCESS_KEY_ID'],
        aws_secret_access_key=env['R2_SECRET_ACCESS_KEY'],
        region_name='auto')
    body = json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8')
    s3.put_object(
        Bucket=env.get('R2_BUCKET', 'novel-data'),
        Key=key, Body=body,
        ContentType='application/json',
        CacheControl='no-cache, no-store, must-revalidate')

# ─── LLM ───

def get_llm_config():
    with open('/root/.hermes/config.yaml') as f:
        cfg = yaml.safe_load(f)
    m = cfg.get('model', {})
    return m.get('base_url', ''), m.get('api_key', ''), m.get('default', '')

LLM_API_BASE, LLM_API_KEY, _ = get_llm_config()

def call_llm(prompt, max_tokens=500, temperature=0.4):
    body = json.dumps({
        'model': os.environ.get('HL_MODEL', 'Qwen/Qwen3-32B'),
        'messages': [{'role': 'user', 'content': prompt}],
        'max_tokens': max_tokens,
        'temperature': temperature
    }).encode()
    req = urllib.request.Request(
        f'{LLM_API_BASE}/chat/completions',
        data=body,
        headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {LLM_API_KEY}'})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                result = json.loads(resp.read())
            return result['choices'][0]['message']['content'].strip()
        except Exception as e:
            print(f'  [LLM attempt {attempt+1} failed: {e}]')
            if attempt < 2: time.sleep(5 * (attempt + 1))
    return None

# ─── YAML Loaders ───

def load_yaml(path):
    if not os.path.exists(path):
        return None
    try:
        with open(path) as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f'    [WARN] YAML parse error in {path}: {e}')
        return None

def _extract_name(val):
    """Extract a string name from either a plain string or a dict like {full, preferred, nicknames}."""
    if isinstance(val, str):
        return val
    if isinstance(val, dict):
        return val.get('preferred') or val.get('full') or str(val)
    return str(val) if val else None

def _extract_aliases(val, primary_name):
    """Extract alias strings from various formats."""
    result = []
    if isinstance(val, list):
        for a in val:
            if isinstance(a, str): result.append(a)
    elif isinstance(val, dict):
        for k in ('nicknames', 'aliases'):
            for a in val.get(k, []):
                if isinstance(a, str): result.append(a)
    seen = {primary_name.lower()}
    out = [primary_name]
    for a in result:
        if a.lower() not in seen:
            out.append(a)
            seen.add(a.lower())
    return out

def parse_characters_yaml(state_dir):
    """Return list of {id, name, aliases, introduction_chapter} from characters.yaml"""
    data = load_yaml(os.path.join(state_dir, 'characters.yaml'))
    if not data:
        return []
    # Handle both list format and dict with 'characters' key
    chars = data
    if isinstance(data, dict):
        chars_data = data.get('characters', data)
        # Could be dict of {id: {name, ...}} or list
        if isinstance(chars_data, dict):
            # Convert dict-of-dicts to list, using key as id
            result = []
            for cid, cdata in chars_data.items():
                if not isinstance(cdata, dict):
                    continue
                raw_name = cdata.get('name')
                if not raw_name:
                    continue
                name = _extract_name(raw_name)
                if not name:
                    continue
                # Skip meta-like keys
                if cid in ('meta', 'config', 'settings'):
                    continue
                raw_aliases = cdata.get('aliases', []) or cdata.get('name', {})
                aliases = _extract_aliases(raw_aliases, name)
                result.append({
                    'id': cid.lower().replace(' ', '_'),
                    'name': name,
                    'aliases': aliases,
                    'introduction_chapter': cdata.get('introduction_chapter') or cdata.get('intro_chapter'),
                })
            return result
        chars = chars_data
    # List format
    if not isinstance(chars, list):
        return []
    result = []
    for c in chars:
        if not c or not isinstance(c, dict):
            continue
        raw_name = c.get('name')
        if not raw_name:
            continue
        name = _extract_name(raw_name)
        if not name:
            continue
        raw_aliases = c.get('aliases', []) or (raw_name if isinstance(raw_name, dict) else [])
        aliases = _extract_aliases(raw_aliases, name)
        result.append({
            'id': c.get('id', name.lower().replace(' ', '_')),
            'name': name,
            'aliases': aliases,
            'introduction_chapter': c.get('introduction_chapter') or c.get('intro_chapter'),
        })
    return result

def _ch_to_num(val):
    """Convert chapter value to int. Handles: 17, '17', 'ch02', 'Ch.3', etc."""
    if isinstance(val, (int, float)):
        return int(val)
    if isinstance(val, str):
        m = re.search(r'(\d+)', val)
        return int(m.group(1)) if m else None
    return None

def _name_to_cid(name, char_ids, char_name_map):
    """Match a character name (e.g. 'Chloe') to a char_id (e.g. 'chloe_park')."""
    name_lower = name.lower().replace(' ', '_')
    if name_lower in char_ids:
        return name_lower
    # Check if name matches the start of any char_id
    for cid in char_ids:
        if cid.startswith(name_lower) or name_lower.startswith(cid):
            return cid
    # Check against primary_name/aliases
    return char_name_map.get(name.lower())

def parse_emotional_debts(state_dir, char_ids, char_name_map):
    """Return {char_id: [chapter_nums]} where character is creditor or debtor"""
    data = load_yaml(os.path.join(state_dir, 'emotional-debts.yaml'))
    if not data:
        return {}
    debts = data
    if isinstance(data, dict):
        debts = data.get('debts', data.get('emotional_debts', []))
    if not isinstance(debts, list):
        debts = []
    result = {cid: [] for cid in char_ids}
    for d in debts:
        if not d or not isinstance(d, dict): continue
        for field in ('creditor', 'debtor'):
            name = d.get(field, '')
            cid = _name_to_cid(name, char_ids, char_name_map)
            if cid and cid in result:
                for ch_field in ('created_chapter', 'incurred_chapter', 'established',
                                 'paid_chapter', 'paid_off_chapter'):
                    ch = _ch_to_num(d.get(ch_field))
                    if ch and ch not in result[cid]:
                        result[cid].append(ch)
    return result

def parse_threads(state_dir, char_ids, char_name_map):
    """Return {char_id: [chapter_nums]} from threads.yaml related_characters"""
    data = load_yaml(os.path.join(state_dir, 'threads.yaml'))
    if not data:
        return {}
    threads = data
    if isinstance(data, dict):
        threads = data.get('threads', [])
    if not isinstance(threads, list):
        threads = []

    result = {cid: [] for cid in char_ids}
    for t in threads:
        if not t or not isinstance(t, dict): continue
        related = t.get('related_characters', []) or []
        for rcid in related:
            rcid_norm = _name_to_cid(rcid, char_ids, char_name_map)
            if rcid_norm and rcid_norm in result:
                for ch_field in ('planted_chapter', 'resolved_chapter',
                                 'established', 'resolved_chapter'):
                    ch = _ch_to_num(t.get(ch_field))
                    if ch and ch not in result[rcid_norm]:
                        result[rcid_norm].append(ch)
    return result

def parse_outline_crown_jewels(outlines_dir, char_ids):
    """Scan outline .md files for CROWN-JEWEL chapters and high-D-code chapters.
    Return {char_id: [chapter_nums]}"""
    result = {cid: [] for cid in char_ids}
    for md_path in glob.glob(os.path.join(outlines_dir, '*.md')):
        with open(md_path) as f:
            text = f.read()
        # Match lines like: **Ch16: "Skin Deep" (CROWN-JEWEL)**
        # or: ### Ch3: "The Garden Handshake" (CROWN-JEWEL)
        for m in re.finditer(r'[#*]*\s*Ch(\d+)[.:]\s*.*?CROWN.JEWEL', text, re.IGNORECASE):
            ch_num = int(m.group(1))
            # CROWN-JEWEL chapters are epic for ALL characters
            for cid in char_ids:
                if ch_num not in result[cid]:
                    result[cid].append(ch_num)
    return result

# ─── Phase 1: Structured Data Builder ───

def _find_novel_dir(slug):
    """Find novel directory with fuzzy matching (case-insensitive, ignore hyphens/underscores)."""
    direct = os.path.join(NOVELS_DIR, slug)
    if os.path.isdir(direct):
        return direct
    # Normalize: lowercase + strip hyphens/underscores
    slug_norm = slug.lower().replace('-', '').replace('_', '')
    for entry in os.listdir(NOVELS_DIR):
        entry_norm = entry.lower().replace('-', '').replace('_', '')
        if entry_norm == slug_norm:
            return os.path.join(NOVELS_DIR, entry)
    return None

def build_from_structured(book_id, slug, catalog):
    """Build characters config from /root/novels/{slug}/state/ files."""
    novel_dir = _find_novel_dir(slug)
    if not novel_dir:
        return None
    state_dir = os.path.join(novel_dir, 'state')
    outlines_dir = os.path.join(novel_dir, 'outlines')

    if not os.path.isdir(state_dir):
        return None

    chars = parse_characters_yaml(state_dir)
    if not chars:
        return None

    char_ids = [c['id'] for c in chars]
    # Build name-to-id map for fuzzy matching in debts/threads
    char_name_map = {}
    for c in chars:
        char_name_map[c['name'].lower()] = c['id']
        for a in c.get('aliases', []):
            char_name_map[a.lower()] = c['id']
    print(f'    Found {len(chars)} characters in characters.yaml')

    # Gather epic chapters from all sources
    debt_chapters = parse_emotional_debts(state_dir, char_ids, char_name_map)
    thread_chapters = parse_threads(state_dir, char_ids, char_name_map)
    crown_chapters = parse_outline_crown_jewels(outlines_dir, char_ids)

    # Get chapter titles for display
    ch_titles = {}
    for ch in catalog.get('chapters', []):
        ch_titles[ch['chapter_id']] = ch.get('title', f'Chapter {ch["chapter_id"]}')

    # Build final config
    result = {}
    for c in chars:
        cid = c['id']

        # Priority ordering for epic chapters:
        # 1. introduction_chapter (most iconic)
        # 2. emotional-debt chapters (personal turning points)
        # 3. thread chapters (key plot moments)
        # 4. CROWN-JEWEL chapters (shared climaxes) — only fill remaining slots
        priority_chapters = []

        intro = c.get('introduction_chapter')
        if intro:
            priority_chapters.append(intro)

        for ch in debt_chapters.get(cid, []):
            if ch not in priority_chapters:
                priority_chapters.append(ch)

        for ch in thread_chapters.get(cid, []):
            if ch not in priority_chapters:
                priority_chapters.append(ch)

        for ch in crown_chapters.get(cid, []):
            if ch not in priority_chapters:
                priority_chapters.append(ch)

        selected = priority_chapters[:5]

        # Build aliases: name + explicit aliases, deduplicated
        aliases = [c['name']] + [a for a in c['aliases'] if a != c['name']]

        # Build epic_nodes with chapter titles
        epic_nodes = []
        for ch_num in selected:
            title = ch_titles.get(ch_num, f'Ch.{ch_num}')
            # Shorten title for the dossier display
            short = re.sub(r'^Chapter\s+\d+:\s*', '', title)
            short = short[:50] if len(short) > 50 else short
            if not short.strip():
                short = f'Ch.{ch_num}'
            epic_nodes.append({
                'title': f'📖 {short}',
                'url': f'/novel/{book_id}/{ch_num}'
            })

        result[cid] = {
            'primary_name': c['name'],
            'aliases': aliases,
            'dossier': {'title': c['name'], 'epic_nodes': epic_nodes}
        }
    # Enrich epic titles with LLM
    use_llm = '--no-llm-enrich' not in sys.argv
    if use_llm:
        print(f'    Enriching epic titles with LLM...')
        result = enrich_epic_titles_with_llm(book_id, result)
    return result

# ─── Epic Title Enrichment ───

def enrich_epic_titles_with_llm(book_id, result):
    """Replace chapter-title-based epic_nodes with 2-3 word dramatic descriptions via LLM.
    All characters in one LLM call for efficiency."""
    # Pre-fetch all unique chapters needed
    all_ch_nums = set()
    for cid, char_data in result.items():
        for node in char_data['dossier'].get('epic_nodes', []):
            m = re.search(r'/(\d+)$', node['url'])
            if m:
                all_ch_nums.add(m.group(1))

    ch_cache = {}
    print(f'    Fetching {len(all_ch_nums)} chapters from R2...')
    for ch_num in all_ch_nums:
        ch_data = r2_get(f'{book_id}/{ch_num}.json')
        if ch_data:
            content = '\n'.join(ch_data.get('content', []))[:500]
            hl = ch_data.get('highlight', '')
            ch_cache[ch_num] = f"Ch{ch_num}: {hl}\n{content}"

    # Build one prompt for all characters
    chars_text = ''
    char_list = []
    for cid, char_data in result.items():
        nodes = char_data['dossier'].get('epic_nodes', [])
        if not nodes:
            continue
        char_name = char_data['primary_name']
        ch_list = []
        for node in nodes:
            m = re.search(r'/(\d+)$', node['url'])
            if m:
                ch_list.append(ch_cache.get(m.group(1), ''))
        chars_text += f'\n## {char_name}\n' + '\n---\n'.join(ch_list) + '\n'
        char_list.append({'id': cid, 'name': char_name, 'count': len(nodes)})

    if not char_list:
        return result

    # Single LLM call for all characters
    prompt = f"""For each character below, write a 2-3 word dramatic label per chapter describing what happens TO them.
Rules: No subject name, must be dramatic (fate turns, betrayals, revelations), 2-3 words each.
Return ONLY valid JSON: {{"char_id": ["label1", "label2", ...]}}

{chars_text}

Return JSON:"""

    print(f'    LLM enriching {len(char_list)} characters...')
    llm_out = call_llm(prompt, max_tokens=400, temperature=0.3)
    if not llm_out:
        return result

    # Parse JSON
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
            except json.JSONDecodeError:
                print(f'    [WARN] Could not parse LLM enrich output')
                return result
        else:
            return result

    # Apply labels
    for ci in char_list:
        cid = ci['id']
        labels = parsed.get(cid, parsed.get(ci['name'], []))
        nodes = result[cid]['dossier'].get('epic_nodes', [])
        if isinstance(labels, list) and len(labels) == len(nodes):
            for i, label in enumerate(labels):
                if isinstance(label, str) and label.strip():
                    nodes[i]['title'] = f'📖 {label.strip()}'

    return result

def build_from_llm(book_id, book_title, catalog):
    """Use LLM to extract characters from chapter highlights + sample content."""
    chapters = catalog.get('chapters', [])
    if not chapters:
        return None

    ch_info = []
    for ch in chapters[:5]:
        ch_id = ch['chapter_id']
        ch_data = r2_get(f'{book_id}/{ch_id}.json')
        content = ''
        hl = ''
        if ch_data:
            hl = ch_data.get('highlight', '')
            content = '\n'.join(ch_data.get('content', []))[:2000]
        ch_info.append(f"--- Chapter {ch_id}: {ch.get('title','')} ---\nHighlight: {hl}\n{content}")

    sample_text = '\n\n'.join(ch_info)

    all_hl = []
    for ch in chapters:
        ch_id = ch['chapter_id']
        ch_data = r2_get(f'{book_id}/{ch_id}.json')
        hl = ch_data.get('highlight', '') if ch_data else ''
        all_hl.append({'id': ch_id, 'title': ch.get('title',''), 'hl': hl})

    hl_text = '\n'.join(
        f"Ch{c['id']}: {c['hl'] or '(none)'}" for c in all_hl
    )

    ch_titles = {ch['chapter_id']: ch.get('title', '') for ch in chapters}
    prompt = f"""Analyze this novel "{book_title}" and extract the core characters.

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
- aliases: include the full name, first name, and any titles/nicknames used
- epic_chapters: pick up to 5 chapters where this character has a pivotal moment
  (first appearance, emotional climax, betrayal, reunion, etc.)
- Use chapter numbers from the highlights list"""

    print(f'    Calling LLM for character extraction...')
    llm_output = call_llm(prompt, max_tokens=800)
    if not llm_output:
        print(f'    [FAIL] LLM returned nothing')
        return None

    # Parse LLM JSON output
    llm_output = re.sub(r'^```(?:json)?\s*', '', llm_output.strip())
    llm_output = re.sub(r'\s*```\s*$', '', llm_output)
    llm_output = re.sub(r'<think>.*?</think>', '', llm_output, flags=re.DOTALL)
    try:
        parsed = json.loads(llm_output)
    except json.JSONDecodeError:
        m = re.search(r'\{[\s\S]*\}', llm_output)
        if m:
            try:
                parsed = json.loads(m.group())
            except json.JSONDecodeError:
                print(f'    [FAIL] Could not parse LLM JSON')
                return None
        else:
            print(f'    [FAIL] No JSON found in LLM output')
            return None

    char_list = parsed.get('characters', [])
    if not char_list:
        print(f'    [FAIL] No characters in LLM output')
        return None

    result = {}
    for c in char_list:
        cid = c.get('id', c['name'].lower().replace(' ', '_'))
        aliases = [c['name']] + [a for a in c.get('aliases', []) if a != c['name']]
        epic_chs = c.get('epic_chapters', [])[:5]
        epic_nodes = []
        for ch_num in epic_chs:
            title = ch_titles.get(ch_num, f'Ch.{ch_num}')
            short = re.sub(r'^Chapter\s+\d+:\s*', '', title)[:50] or f'Ch.{ch_num}'
            epic_nodes.append({
                'title': f'📖 {short}',
                'url': f'/novel/{book_id}/{ch_num}'
            })
        result[cid] = {
            'primary_name': c['name'],
            'aliases': aliases,
            'dossier': {'title': c['name'], 'epic_nodes': epic_nodes}
        }
    # Enrich epic titles with LLM
    use_llm = '--no-llm-enrich' not in sys.argv
    if use_llm:
        print(f'    Enriching epic titles with LLM...')
        result = enrich_epic_titles_with_llm(book_id, result)
    return result


def enrich_existing(book_id):
    """Read characters_{book_id}.json from R2, enrich epic titles, re-upload."""
    env = load_env()
    key = f'characters_{book_id}.json'
    result = r2_get(key)
    if not result:
        print(f'    No existing {key} found')
        return False

    enriched = enrich_epic_titles_with_llm(book_id, result)
    if enriched:
        r2_put(key, enriched, env)
        print(f'    Uploaded enriched {key}')
        return True
    return False

def main():
    # Enrich mode: just update titles on existing characters files
    if '--enrich' in sys.argv:
        target_book = None
        for arg in sys.argv[1:]:
            if arg.startswith('--book='):
                target_book = [int(x) for x in arg.split('=')[1].split(',')]
        books = r2_get('books.json')
        if not books:
            print('ERROR: Cannot fetch books.json'); sys.exit(1)
        for b in books:
            if b.get('lang') not in ('english','en'): continue
            bid = b['id']
            if target_book and bid not in target_book: continue
            print(f'📚 Book {bid}: {b["title"]}')
            try:
                enrich_existing(bid)
            except Exception as e:
                print(f'    [ERROR] {e}')
            time.sleep(1)
        return

    env = load_env()
    dry_run = '--dry-run' in sys.argv
    target_book = None
    for arg in sys.argv[1:]:
        if arg.startswith('--book='):
            target_book = [int(x) for x in arg.split('=')[1].split(',')]

    books = r2_get('books.json')
    if not books:
        print('ERROR: Cannot fetch books.json')
        sys.exit(1)

    en_books = [b for b in books if b.get('lang') in ('english', 'en')]
    total_ok = total_skip = total_fail = 0

    for book in en_books:
        book_id = book['id']
        book_title = book['title']
        slug = book.get('slug', '')
        if target_book and book_id not in target_book:
            continue

        print(f'\n📚 Book {book_id}: {book_title}')

        existing = r2_get(f'characters_{book_id}.json')
        if existing and '--force' not in sys.argv:
            print(f'    [SKIP] characters_{book_id}.json already exists')
            total_skip += 1
            continue

        catalog = r2_get(f'catalog_{book_id}.json')
        if not catalog:
            print(f'    [SKIP] No catalog')
            total_skip += 1
            continue

        # Phase 1: try structured data
        config = None
        try:
            config = build_from_structured(book_id, slug, catalog) if slug else None
        except Exception as e:
            print(f'    [WARN] Structured data error: {e}')

        # Phase 2: LLM fallback
        if not config:
            print(f'    No structured data, using LLM...')
            try:
                config = build_from_llm(book_id, book_title, catalog)
            except Exception as e:
                print(f'    [WARN] LLM error: {e}')

        if not config:
            print(f'    [FAIL] Could not generate characters')
            total_fail += 1
            continue

        char_count = len(config)
        print(f'    ✅ Generated {char_count} characters')

        # Upload
        if not dry_run:
            try:
                r2_put(f'characters_{book_id}.json', config, env)
                print(f'    Uploaded characters_{book_id}.json')
            except Exception as e:
                print(f'    [UPLOAD ERROR] {e}')
                total_fail += 1
                continue
        else:
            print(f'    [DRY RUN] would upload')
            print(json.dumps(config, indent=2, ensure_ascii=False)[:500])

        total_ok += 1
        time.sleep(0.5)

    print(f'\n{"="*50}')
    print(f'Done! Generated: {total_ok}, Skipped: {total_skip}, Failed: {total_fail}')

if __name__ == '__main__':
    main()
