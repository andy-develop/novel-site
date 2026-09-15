#!/usr/bin/env python3
"""Audit chapter files: H1 format, special chars in titles, hash-leading lines."""
import glob, re, os

d = '/root/novels/tea-with-the-devil/chapters'
bad_h1, bad_chars, hash_body, thin = [], [], [], []
for f in sorted(glob.glob(os.path.join(d, 'ch*.md'))):
    n = os.path.basename(f)
    lines = open(f, encoding='utf-8').read().splitlines()
    if not lines or not lines[0].startswith('# '):
        bad_h1.append((n, lines[0][:60] if lines else 'EMPTY'))
        continue
    h1 = lines[0][2:].strip()
    m = re.match(r'^Chapter (\d+):', h1)
    num_ok = m and int(m.group(1)) == int(n[2:5])
    if not num_ok:
        bad_h1.append((n, h1[:60]))
    if re.search(r'[#—–&:()]', h1):
        bad_chars.append((n, h1))
    if re.search(r'— Day|\bDay \d+\.$', h1):
        bad_chars.append((n, 'DAYMARK: ' + h1))
    for i, ln in enumerate(lines[1:], 2):
        if ln.startswith('#'):
            hash_body.append((n, i, ln[:50]))
    w = len(re.findall(r'\S+', ' '.join(lines)))
    if w < 1300:
        thin.append((n, w))

print("bad H1 (missing/num mismatch):", bad_h1 if bad_h1 else "none")
print("special chars / day marks in titles:", bad_chars if bad_chars else "none")
print("hash-leading body lines:", hash_body if hash_body else "none")
print("thin chapters (<1300w):", thin if thin else "none")
