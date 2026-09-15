#!/usr/bin/env python3
"""Audit chapter files: H1 titles, word counts, format violations."""
import re, sys, os

DIR = '/root/novels/the-red-camellia/chapters'
EXPECTED = {
1:"Red Dress on the Water",2:"Funeral Flowers",3:"Invented Heiress",4:"Rooftop Blood",
5:"The Numbers Don't Lie",6:"Camellia Blooms",7:"The Servant's Stairs",8:"The Kiss That Knew Too Much",
9:"Two Truths",10:"Roxy's Little Leak",11:"Tea with the Matriarch",12:"The Golden Cage",
13:"Nico's Version",14:"The Paper Trail",15:"Midnight Vault",16:"Who Leaked the Night",
17:"Courtesan",18:"The Ultimatum",19:"The Cruelest Kindness",20:"The Drowning",
21:"Letters From the Dead",22:"Ghost on the Subway",23:"Walt's Version",24:"First Blood",
25:"Her Own Voice",26:"Standing Proof",27:"Empire of Dust",28:"Camellia",
}

files = sorted(f for f in os.listdir(DIR) if re.fullmatch(r'ch\d{3}\.md', f))
nums = sorted(int(re.search(r'ch(\d{3})', f).group(1)) for f in files)
print(f"files: {len(files)}  range: {nums[0] if nums else '-'}..{nums[-1] if nums else '-'}")

missing = [n for n in EXPECTED if n not in nums]
print("missing chapters:", missing if missing else "none")

total = 0
problems = []
for n in nums:
    path = os.path.join(DIR, f"ch{n:03d}.md")
    lines = open(path, encoding='utf-8').read().split('\n')
    # H1 check
    h1 = None
    if lines and lines[0].startswith('# '):
        h1 = lines[0][2:].strip()
    expected_h1 = f"Chapter {n}: {EXPECTED[n]}"
    if h1 != expected_h1:
        problems.append(f"ch{n:03d}: H1={h1!r} EXPECTED={expected_h1!r}")
    # word count
    words = len(re.findall(r"[\w']+", open(path, encoding='utf-8').read()))
    total += words
    if words < 1600:
        problems.append(f"ch{n:03d}: {words} words < 1600")
    # format violations
    body = lines[1:]
    for i, line in enumerate(body, start=2):
        s = line.strip()
        if s.startswith('#'):
            problems.append(f"ch{n:03d}: hash-leading line {i}: {s[:40]}")
        if s in ('---', '***', '___') or (s.startswith('***') and len(s) <= 4):
            problems.append(f"ch{n:03d}: scene divider line {i}")
        if '*' in s:
            problems.append(f"ch{n:03d}: asterisk line {i}: {s[:40]}")
    # title char check
    for ch in '#—–&:()':
        if ch in EXPECTED[n]:
            problems.append(f"ch{n:03d}: forbidden char {ch!r} in title")
    print(f"ch{n:03d}: {words:5d} words | {h1}")

print(f"\nTOTAL WORDS: {total}")
print(f"avg/ch: {total//max(len(nums),1)}")
print("PROBLEMS:" if problems else "NO PROBLEMS")
for p in problems:
    print(" -", p)
