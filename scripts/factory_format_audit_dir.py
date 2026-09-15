#!/usr/bin/env python3
"""Audit chapter format contract for any novel dir: H1s, titles, banned chars, body lines."""
import re, os, sys

d = sys.argv[1] if len(sys.argv) > 1 else "/root/novels/i-am-no-bird/chapters"
files = sorted(f for f in os.listdir(d) if re.fullmatch(r"ch\d{3}\.md", f))
print(f"files: {len(files)}")
if not files:
    sys.exit("no chapters")

BANNED = ["—", "–", "&", ":", "(", ")", "#", "*", "_", ">", "|"]
problems = []
for f in files:
    n = int(re.search(r"ch(\d{3})", f).group(1))
    lines = open(os.path.join(d, f), encoding="utf-8").read().splitlines()
    if not lines or not lines[0].startswith("# Chapter "):
        problems.append(f"{f}: missing H1: {lines[0] if lines else 'EMPTY'}")
        continue
    h1 = lines[0][2:].strip()
    if not h1.startswith(f"Chapter {n}:"):
        problems.append(f"{f}: H1 prefix wrong: {h1!r}")
    title_part = h1.split(":", 1)[1].strip() if ":" in h1 else h1
    for ch in BANNED:
        if ch in title_part:
            problems.append(f"{f}: banned char {ch!r} in title: {title_part!r}")
    for i, ln in enumerate(lines[1:], start=2):
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#"):
            problems.append(f"{f}: line {i} hash-leading: {s[:60]!r}")
        if any(b in ln for b in ["**", "__"]):
            problems.append(f"{f}: line {i} markdown emphasis: {s[:60]!r}")
        if "—" in ln or "–" in ln:
            problems.append(f"{f}: line {i} em/en dash")
        if ln.startswith(("* ", "- ", "> ")):
            problems.append(f"{f}: line {i} list/quote: {s[:60]!r}")

print("PROBLEMS:" if problems else "CLEAN")
for p in problems[:60]:
    print(" ", p)
print(f"total_problems={len(problems)}")
