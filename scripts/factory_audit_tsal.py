#!/usr/bin/env python3
"""Audit chapters: H1 format, banned title chars, word counts, markdown violations."""
import os, re, sys

DIR = '/root/novels/the-scent-of-a-lie/chapters'
files = sorted(f for f in os.listdir(DIR) if re.fullmatch(r'ch\d{3}\.md', f))
print('n_files:', len(files), '| first:', files[0], '| last:', files[-1])
total = 0
title_issues = []
body_issues = []
for f in files:
    path = os.path.join(DIR, f)
    with open(path, encoding='utf-8') as fh:
        lines = fh.read().split('\n')
    # H1
    h1 = lines[0]
    if not h1.startswith('# Chapter '):
        title_issues.append((f, 'BAD H1: ' + h1[:60]))
    else:
        m = re.match(r'# Chapter (\d+): (.*)', h1)
        if not m:
            title_issues.append((f, 'BAD H1 fmt: ' + h1[:60]))
        else:
            num, title = int(m.group(1)), m.group(2)
            if re.search(r'[#—–&:()\.]', title):
                title_issues.append((f, f'banned char in title: {title}'))
            if num != int(f[2:5]):
                title_issues.append((f, f'H1 number {num} != filename {f}'))
    # body lines starting with #
    for i, ln in enumerate(lines[1:], 2):
        if ln.startswith('#'):
            body_issues.append((f, f'line {i} starts with #: {ln[:50]}'))
    # asterisks / markdown
    body = '\n'.join(lines[1:])
    for m in re.finditer(r'\*{1,3}', body):
        ctx = body[max(0, m.start()-25):m.end()+25].replace('\n', ' ')
        body_issues.append((f, f'asterisks: ...{ctx}...'))
        break
    for pat in ['---', '***', '## ']:
        if pat in body:
            body_issues.append((f, f'contains {pat!r}'))
    # word count
    words = len(body.split())
    total += words
    if words < 1300:
        title_issues.append((f, f'THIN {words}w'))
print('total_words:', total)
print('TITLE ISSUES:', len(title_issues))
for i in title_issues[:20]:
    print(' ', i)
print('BODY ISSUES:', len(body_issues))
seen = set()
for i in body_issues:
    key = i[0] + i[1][:20]
    if key not in seen:
        seen.add(key)
        print(' ', i)
