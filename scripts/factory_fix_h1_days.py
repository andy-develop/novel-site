#!/usr/bin/env python3
"""Strip ' — Day ...' suffixes from chapter H1 lines: '# Chapter N: Title — Day 0.' -> '# Chapter N: Title'."""
import re, glob, sys

files = sorted(glob.glob("/root/novels/riverborn/chapters/ch*.md"))
fixed = []
for f in files:
    with open(f, encoding="utf-8") as fh:
        lines = fh.readlines()
    if not lines:
        continue
    m = re.match(r"^(# Chapter \d+: .*?) — Day.*$", lines[0].rstrip("\n"))
    if m:
        lines[0] = m.group(1) + "\n"
        with open(f, "w", encoding="utf-8") as fh:
            fh.writelines(lines)
        fixed.append((f.split("/")[-1], lines[0].strip()))
    elif "# Chapter" in lines[0]:
        fixed.append((f.split("/")[-1], "NOCHANGE: " + lines[0].strip()))
    else:
        fixed.append((f.split("/")[-1], "NOT-H1!"))

for name, h1 in fixed:
    print(name, "|", h1)

# audit: any em-dash remaining in H1 lines?
bad = [f for f in files for l in open(f, encoding="utf-8").readlines()[:1] if "—" in l]
print("REMAINING_EMDASH_IN_H1:", bad if bad else "none")
