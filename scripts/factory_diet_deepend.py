#!/usr/bin/env python3
"""Quick prose-diet audit: eyes count, suddenly count, long paragraphs."""
import re, glob, os

d = '/root/novels/the-deep-end/chapters'
issues = []
for f in sorted(glob.glob(os.path.join(d, 'ch*.md'))):
    txt = open(f, encoding='utf-8').read()
    name = os.path.basename(f)
    eyes = len(re.findall(r'\beyes\b', txt))
    sud = len(re.findall(r'\bsuddenly\b', txt, re.I))
    paras = [p for p in txt.split('\n') if p.strip() and not p.startswith('#')]
    longp = [len(p.split('\n')) for p in re.split(r'\n\n+', txt) if p.strip() and not p.startswith('#')]
    maxlines = max([p.count('\n')+1 for p in re.split(r'\n\n+', txt) if p.strip() and not p.startswith('#')] or [0])
    flags = []
    if eyes > 3: flags.append(f"eyes={eyes}")
    if sud > 2: flags.append(f"suddenly={sud}")
    if maxlines > 6: flags.append(f"maxpara={maxlines}lines")
    print(f"{name}: eyes={eyes} suddenly={sud} maxpara={maxlines} {' '.join(flags)}")
