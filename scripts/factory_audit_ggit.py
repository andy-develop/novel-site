#!/usr/bin/env python3
"""Final format audit for upload: H1 contract, no markdown violations, titles clean."""
import re, glob, sys

files = sorted(glob.glob('/root/novels/green-gables-is-trending/chapters/ch*.md'))
errors = []
the_count = 0
total_words = 0
for f in files:
    n = int(re.search(r'ch(\d+)\.md', f).group(1))
    with open(f, encoding='utf-8') as fh:
        lines = fh.read().split('\n')
    # H1 contract
    h1 = lines[0]
    if not re.match(r'^# Chapter \d+: .+', h1):
        errors.append(f'{f}: bad H1: {h1!r}')
    if f'# Chapter {n}: ' not in h1:
        errors.append(f'{f}: H1 chapter number mismatch: {h1!r}')
    # body violations
    for i, ln in enumerate(lines[1:], start=2):
        if ln.startswith('#'):
            errors.append(f'{f}:{i}: hash-leading body line: {ln!r}')
        if '*' in ln or '_' in ln.replace('_', '', 0) and '**' in ln:
            if '*' in ln:
                errors.append(f'{f}:{i}: asterisk found')
        if re.match(r'^\s*(---|\*\*\*|===)\s*$', ln):
            errors.append(f'{f}:{i}: scene divider')
    # title special chars
    title = h1.split(': ', 1)[1] if ': ' in h1 else h1
    for ch in ['—', '–', '&', '#', '(', ')']:
        if ch in title:
            errors.append(f'{f}: special char {ch!r} in title: {title!r}')
    if title.startswith('The '):
        the_count += 1
    words = len(re.findall(r"[A-Za-z0-9']+", ' '.join(lines)))
    total_words += words

print(f'files={len(files)} total_words={total_words} the_titles={the_count}/{len(files)} ({100.0*the_count/len(files):.1f}%)')
if errors:
    print('ERRORS:')
    for e in errors[:30]:
        print(' ', e)
    sys.exit(1)
print('AUDIT PASS')
