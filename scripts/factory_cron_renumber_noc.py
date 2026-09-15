#!/usr/bin/env python3
"""Insert 6 POV expansion chapters into the 24 main chapters, renumber to 30."""
import os, re, shutil, sys

BASE = '/root/novels/no-one-is-coming/chapters'
EXP = '/root/novels/no-one-is-coming/outlines/expansion'

# final chapter number -> source (existing chNNN or expansion file)
final_map = {}
for n in range(1, 19):      # ch001-018 stay
    final_map[n] = f'ch{n:03d}.md'
final_map[19] = 'cole-version.md'
final_map[20] = 'manny-version.md'
for src, fin in [(19, 21), (20, 22), (21, 23)]:   # main 19-21 -> 21-23
    final_map[fin] = f'ch{src:03d}.md'
final_map[24] = 'del-version.md'
final_map[25] = 'sasha-version.md'
final_map[26] = 'ch022.md'
final_map[27] = 'tobi-version.md'
final_map[28] = 'ch023.md'
final_map[29] = 'yara-version.md'
final_map[30] = 'ch024.md'

assert sorted(final_map) == list(range(1, 31)), "map must cover 1..30"

# sanity: sources exist
for fin, src in final_map.items():
    p = os.path.join(EXP, src) if src.endswith('.md') and not re.fullmatch(r'ch\d{3}\.md', src) else os.path.join(BASE, src)
    assert os.path.exists(p), f"missing source {src}"

# 1. move all sources to temp names in reverse final order (no collisions)
tmp = {}
for fin in sorted(final_map, reverse=True):
    src = final_map[fin]
    srcp = os.path.join(EXP, src) if not re.fullmatch(r'ch\d{3}\.md', src) else os.path.join(BASE, src)
    dst = os.path.join(BASE, f'ch{fin:03d}.tmp')
    shutil.copy2(srcp, dst)
    tmp[fin] = dst
    print(f"staged {src} -> ch{fin:03d}.tmp")

# 2. commit: replace existing chNNN.md, then rewrite H1 numbers
for fin, dst in tmp.items():
    final_path = os.path.join(BASE, f'ch{fin:03d}.md')
    os.replace(dst, final_path)

# 3. rewrite H1 prefix to match file number
pat = re.compile(r'^# Chapter \d+:')
for fin in range(1, 31):
    p = os.path.join(BASE, f'ch{fin:03d}.md')
    lines = open(p, encoding='utf-8').read().split('\n')
    if lines and lines[0].startswith('# Chapter'):
        lines[0] = pat.sub(f'# Chapter {fin}:', lines[0])
    else:
        print(f"!! ch{fin:03d} H1 missing or wrong: {lines[0] if lines else 'EMPTY'}")
    open(p, 'w', encoding='utf-8').write('\n'.join(lines))

# 4. verify
files = sorted(f for f in os.listdir(BASE) if re.fullmatch(r'ch\d{3}\.md', f))
print("file count:", len(files))
bad = 0
for f in files:
    n = int(re.search(r'ch(\d{3})', f).group(1))
    first = open(os.path.join(BASE, f), encoding='utf-8').readline().strip()
    if not first.startswith(f'# Chapter {n}:'):
        print(f"!! {f} H1: {first!r}")
        bad += 1
    if '—' in first or '&' in first or ':' in first.replace(f'# Chapter {n}:', ''):
        print(f"!! {f} H1 has special chars: {first!r}")
        bad += 1
print("H1 bad:", bad)
