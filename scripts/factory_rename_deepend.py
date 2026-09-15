#!/usr/bin/env python3
"""Rename 4 H1 titles in THE DEEP END to cut TheX ratio from 42% to 25%."""
import re

changes = {
    8:  "# Chapter 8: File 52.8",
    15: "# Chapter 15: Plus One",
    17: "# Chapter 17: Long Con",
    18: "# Chapter 18: Zero Hour",
}
for num, new_h1 in changes.items():
    path = f"/root/novels/the-deep-end/chapters/ch{num:03d}.md"
    lines = open(path, encoding='utf-8').read().split('\n')
    old = lines[0].strip()
    lines[0] = new_h1
    open(path, 'w', encoding='utf-8').write('\n'.join(lines))
    print(f"ch{num:03d}: {old!r} -> {new_h1!r}")
