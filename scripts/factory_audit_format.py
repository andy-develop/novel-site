#!/usr/bin/env python3
"""Audit chapter files: H1 format, forbidden markdown, word counts."""
import os, re, sys

DIR = "/root/novels/the-truth-sickness/chapters"
expected = {
    1: "Graduation Day", 2: "Sneeze", 3: "Perfect", 4: "What the Doctor Said",
    5: "Diagnosis", 6: "Disowned", 7: "Run", 8: "Echo's Cabin", 9: "Pruned",
    10: "Can You Lie for Me", 11: "IPO", 12: "The Truth Sickness", 13: "Lily's File",
    14: "Press Conference", 15: "Counter Offer", 16: "Thirty Days", 17: "Archive",
    18: "The Orchard's Lawyer", 19: "Live at Nine", 20: "Mom's Version", 21: "Rose's Version",
    22: "Viral", 23: "Graduation Day Two", 24: "The Sanctuary", 25: "Interview",
    26: "Unpruned", 27: "Open Air",
}

problems = []
files = sorted(f for f in os.listdir(DIR) if re.fullmatch(r"ch\d{3}\.md", f))
print(f"FILES: {len(files)}")
for f in files:
    n = int(f[2:5])
    path = os.path.join(DIR, f)
    text = open(path, encoding="utf-8").read()
    lines = text.split("\n")
    words = len(text.split())
    # H1 check
    h1 = lines[0].strip()
    want = f"# Chapter {n}: {expected.get(n, '???')}"
    if h1 != want:
        problems.append(f"{f}: H1={h1!r} want={want!r}")
    # em-dash / special chars in the TITLE portion (after '# Chapter N: ')
    m = re.match(r"# Chapter \d+: (.*)", h1)
    if m:
        title = m.group(1)
        if re.search(r"[—–&:()#]", title):
            problems.append(f"{f}: TITLE special chars: {title}")
    else:
        problems.append(f"{f}: H1 malformed: {h1!r}")
    # body hash-leading lines
    for i, ln in enumerate(lines[1:], 2):
        if ln.startswith("#"):
            problems.append(f"{f}: line {i} starts with #: {ln[:60]}")
    # asterisks / dividers
    for i, ln in enumerate(lines, 1):
        if re.search(r"\*{2,}", ln):
            problems.append(f"{f}: line {i} has **: {ln[:60]}")
        if ln.strip() in ("***", "---", "***", "❖", "~~~"):
            problems.append(f"{f}: line {i} scene divider")
    # word floor
    if words < 1300:
        problems.append(f"{f}: LOW WORDS {words}")
    print(f"{f}: {words} words | {h1[:60]}")

print(f"\nTOTAL WORDS: {sum(len(open(os.path.join(DIR,f),encoding='utf-8').read().split()) for f in files)}")
print(f"\nPROBLEMS: {len(problems)}")
for p in problems:
    print(" -", p)
sys.exit(1 if problems else 0)
