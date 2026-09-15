#!/usr/bin/env python3
"""Insert /tmp/marlene.md as ch010 and /tmp/jonas.md as ch020, renumbering
the rest. Usage: python3 renumber-insert.py <dir>"""
import os, re, sys, shutil

d = sys.argv[1]
ch = os.path.join(d, "chapters")
files = sorted(f for f in os.listdir(ch) if re.fullmatch(r'ch\d{3}\.md', f))
nums = sorted(int(f[2:5]) for f in files)
assert nums == list(range(1, 25)), f"unexpected chapter set: {nums}"

# 1. shift old 19-24 -> 21-26 (reverse)
for n in range(24, 18, -1):
    os.rename(os.path.join(ch, f"ch{n:03d}.md"), os.path.join(ch, f"ch{n+2:03d}.md"))
# 2. shift old 10-18 -> 11-19 (reverse)
for n in range(18, 9, -1):
    os.rename(os.path.join(ch, f"ch{n:03d}.md"), os.path.join(ch, f"ch{n+1:03d}.md"))
# 3. insert new chapters
shutil.copy('/tmp/marlene.md', os.path.join(ch, "ch010.md"))
shutil.copy('/tmp/jonas.md', os.path.join(ch, "ch020.md"))

# 4. rewrite H1 numbers to match filenames
for f in sorted(os.listdir(ch)):
    if not re.fullmatch(r'ch\d{3}\.md', f):
        continue
    newnum = int(f[2:5])
    p = os.path.join(ch, f)
    lines = open(p, encoding='utf-8').read().split('\n')
    if lines and lines[0].startswith('# Chapter '):
        lines[0] = re.sub(r'^# Chapter \d+:', f'# Chapter {newnum}:', lines[0])
    else:
        print(f"!! {f}: no H1, prepending")
        lines.insert(0, f"# Chapter {newnum}:")
    open(p, 'w', encoding='utf-8').write('\n'.join(lines))

print("renumber done:", sorted(os.listdir(ch)))
