#!/usr/bin/env python3
"""Audit chapter files: H1 extraction, forbidden chars, markdown pollution."""
import re, glob

bad_titles = []
bad_body = []
titles = []
for f in sorted(glob.glob('/root/novels/delusion-girl/chapters/ch*.md')):
    n = int(re.search(r'ch(\d+)\.md', f).group(1))
    lines = open(f, encoding='utf-8').read().splitlines()
    h1 = lines[0].strip() if lines else ''
    if not h1.startswith('# Chapter '):
        bad_titles.append((n, 'BAD H1: ' + h1[:80]))
        continue
    title = h1[2:].strip()
    titles.append(title)
    # forbidden chars in title (apostrophes OK)
    if re.search(r'[#—–&:()\[\]]', title):
        bad_titles.append((n, 'FORBIDDEN CHAR in title: ' + title))
    if not re.match(r'Chapter \d+: .+', title):
        bad_titles.append((n, 'H1 FORMAT WRONG: ' + title))
    # body checks
    for i, ln in enumerate(lines[1:], 2):
        s = ln.strip()
        if s.startswith('#'):
            bad_body.append((n, i, 'hash-line: ' + s[:60]))
        if re.search(r'\*{1,}', ln) and not re.search(r'\*[A-Za-z][^*]{0,40}\*', ln):
            # asterisks that are not inline emphasis markers
            bad_body.append((n, i, 'asterisk: ' + s[:60]))
        if re.match(r'^(\*{3,}|-{3,}|~{3,}|={3,})$', s):
            bad_body.append((n, i, 'scene divider'))

print('TITLES:')
for t in titles:
    print(' ', t)
print('---')
print('TITLE ISSUES:', bad_titles if bad_titles else 'none')
print('BODY ISSUES:', len(bad_body))
for b in bad_body[:40]:
    print('  ch%03d line %d: %s' % b)
# The-opener ratio
the_count = sum(1 for t in titles if re.match(r'^Chapter \d+: The\b', t))
print('---')
print('Total chapters:', len(titles), '| "The X" openers:', the_count, f'({the_count/len(titles)*100:.0f}%)')
