#!/usr/bin/env python3
"""Renumber chapters for then-there-were-four (safe temp-move, python renames)."""
import os, re

d = "/root/novels/then-there-were-four/chapters"
os.chdir(d)

# old -> new number map
moves = {23: 24, 24: 25, 25: 23}

# stage to temp names first (avoid clobber)
staged = {}
for old, new in moves.items():
    src = f"ch{old:03d}.md"
    tmp = f".tmp_{old}.md"
    os.rename(src, tmp)
    staged[tmp] = new

for tmp, new in sorted(staged.items(), key=lambda kv: kv[1]):
    dst = f"ch{new:03d}.md"
    os.rename(tmp, dst)
    # rewrite H1
    with open(dst, encoding="utf-8") as f:
        lines = f.readlines()
    if lines and lines[0].startswith("# Chapter"):
        lines[0] = re.sub(r"^# Chapter \d+: ", f"# Chapter {new}: ", lines[0])
        with open(dst, "w", encoding="utf-8") as f:
            f.writelines(lines)
        print(f"{dst} -> H1: {lines[0].strip()}")
    else:
        print(f"{dst} WARN: no H1 first line")

files = sorted(f for f in os.listdir(d) if re.fullmatch(r"ch\d{3}\.md", f))
print(f"total files: {len(files)}")
print("first lines:", [open(os.path.join(d, f), encoding='utf-8').readline().strip() for f in files])
