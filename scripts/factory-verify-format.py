#!/usr/bin/env python3
"""Verify chapter format contract for upload: H1 first line, plain paragraphs, no markdown."""
import glob, os, re, sys

d = "/root/novels/scarlet-evidence/chapters"
files = sorted(glob.glob(os.path.join(d, "ch*.md")))
expected_titles = {
    1: "The Leak", 2: "Canceled", 3: "The Original", 4: "Watermark",
    5: "The Vote", 6: "Priya's Box", 7: "First Letter", 8: "Seven",
    9: "Investigator", 10: "Expulsion", 11: "Dex", 12: "Inside Man",
    13: "Cole's File", 14: "Nia's Tape", 15: "Gala Invite", 16: "Vault Night",
    17: "Leak Back", 18: "Abuela's Letter", 19: "Sisterhood", 20: "Nia Confesses",
    21: "Gala Night", 22: "The Letter Flips", 23: "The Brand", 24: "Seven Bells",
}
total = 0
errors = []
the_count = 0
for f in files:
    m = re.search(r"ch(\d{3})\.md", f)
    n = int(m.group(1))
    lines = open(f, encoding="utf-8").read().split("\n")
    # strip blank lines at start
    while lines and not lines[0].strip():
        lines.pop(0)
    h1 = lines[0].strip() if lines else ""
    body = [l for l in lines[1:] if l.strip()]
    words = sum(len(l.split()) for l in body)
    total += words
    # H1 check
    expect = f"# Chapter {n}: {expected_titles.get(n, '?')}"
    if h1 != expect:
        errors.append(f"ch{n:03d} H1 mismatch: {h1!r} != {expect!r}")
    # body checks
    for i, l in enumerate(body, 2):
        if l.startswith("#"):
            errors.append(f"ch{n:03d} line {i} starts with #: {l[:60]!r}")
        if re.search(r"\*\*|\*|^---+$|^>", l):
            errors.append(f"ch{n:03d} line {i} markdown: {l[:60]!r}")
        if "—" in l or "–" in l:
            errors.append(f"ch{n:03d} line {i} em/en dash: {l[:60]!r}")
    # title special chars
    t = h1[len(f"# Chapter {n}: "):]
    if re.search(r"[#—–&:()]", t):
        errors.append(f"ch{n:03d} title special char: {t!r}")
    if t.startswith("The "):
        the_count += 1
    print(f"ch{n:03d} {t!r}  {words}w")
print(f"\nTOTAL WORDS: {total}")
print(f"'The X' titles: {the_count}/{len(files)} = {the_count/len(files)*100:.0f}%")
print(f"files: {len(files)}")
if errors:
    print("\nERRORS:")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print("FORMAT OK")
