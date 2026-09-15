#!/usr/bin/env python3
"""Audit SOFT THINGS chapters: H1 contract, body purity, word counts."""
import os, re, sys

D = "/root/novels/soft-things/chapters"
EXPECTED = {
    1: "The Soft One", 2: "Fatta Land", 3: "Auction Night", 4: "Soft Hands",
    5: "The Oracle", 6: "Giant Girl", 7: "The Price", 8: "Rabbits",
    9: "Eclipse Baby", 10: "The Shepherd", 11: "Bloodline", 12: "The Frame",
    13: "The Trial", 14: "The Shutdown", 15: "Counter Offer", 16: "Soft Things",
    17: "Offshore", 18: "Her Mother", 19: "Vanishing", 20: "Posse",
    21: "Livestream", 22: "Falling House", 23: "Rescue", 24: "Mother's Choice",
    25: "All of It", 26: "Buy It Back", 27: "Hutch",
}

total = 0
problems = []
files = sorted(f for f in os.listdir(D) if re.fullmatch(r"ch\d{3}\.md", f))
print(f"files found: {len(files)}")
for f in files:
    n = int(f[2:5])
    path = os.path.join(D, f)
    lines = open(path, encoding="utf-8").read().splitlines()
    body = open(path, encoding="utf-8").read()
    words = len(body.split())
    total += words
    # H1 check
    h1 = lines[0] if lines else ""
    expect_h1 = f"# Chapter {n}: {EXPECTED.get(n, '?')}"
    if h1 != expect_h1:
        problems.append(f"{f}: H1 mismatch -> {h1!r} (expected {expect_h1!r})")
    if "—" in h1 or "–" in h1:
        problems.append(f"{f}: em/en dash in H1")
    for c in "#*_`~|><":
        pass
    # body purity: no lines starting with '#' other than H1, no asterisks, no dividers
    for i, ln in enumerate(lines[1:], 2):
        if ln.startswith("#"):
            problems.append(f"{f}: line {i} starts with #: {ln[:40]!r}")
        if re.fullmatch(r"\s*(\*{3,}|-{3,}|_{3,})\s*", ln):
            problems.append(f"{f}: scene divider at line {i}")
        if "*" in ln or "**" in ln:
            problems.append(f"{f}: asterisk at line {i}: {ln[:40]!r}")
    if words < 1300:
        problems.append(f"{f}: only {words} words (floor 1300)")
    print(f"{f}: {words} words | H1 ok={h1 == expect_h1}")

print(f"TOTAL WORDS: {total}")
print(f"EXPECTED {len(EXPECTED)} chapters; missing: {sorted(set(EXPECTED) - {int(f[2:5]) for f in files})}")
if problems:
    print("PROBLEMS:")
    for p in problems:
        print(" -", p)
else:
    print("NO PROBLEMS")
