#!/usr/bin/env python3
"""Audit chapter format contract for upload. Cron-safe."""
import re, sys, glob, os

d = "/root/novels/tomorrow-girl/chapters"
files = sorted(glob.glob(os.path.join(d, "ch[0-9][0-9][0-9].md")))
print("files:", len(files))
bad_title_chars = re.compile(r"[—–&:()#]|  ")
bad = []
no_h1 = []
hash_body = []
em_special = []
for f in files:
    lines = open(f, encoding="utf-8").read().split("\n")
    h1 = lines[0] if lines else ""
    m = re.match(r"^# Chapter (\d+): (.+)$", h1)
    if not m:
        no_h1.append((os.path.basename(f), h1[:60]))
        continue
    n = int(m.group(1))
    title = m.group(2)
    if bad_title_chars.search(title):
        bad.append((os.path.basename(f), title))
    if re.search(r"—|–", title):
        em_special.append((os.path.basename(f), title))
    # hash-leading body lines (any line starting with # other than H1)
    for i, ln in enumerate(lines[1:], 2):
        if ln.startswith("#"):
            hash_body.append((os.path.basename(f), i, ln[:50]))
print("no H1:", no_h1)
print("bad title chars:", bad)
print("em-dash titles:", em_special)
print("hash body lines:", hash_body)
# title pattern variety: count first words, "The X" ratio
titles = []
for f in files:
    h1 = open(f, encoding="utf-8").readline().strip()
    m = re.match(r"^# Chapter \d+: (.+)$", h1)
    if m:
        titles.append(m.group(1))
the_n = sum(1 for t in titles if t.startswith("The "))
print(f"titles: {len(titles)}, starting 'The ': {the_n} ({the_n/len(titles)*100:.0f}%)")
print("titles:", titles)
