#!/usr/bin/env python3
"""Strip stray asterisks (italic markers) from chapter body text."""
import re, glob

for path in sorted(glob.glob('/root/novels/who-keeps-the-lights-on/chapters/ch*.md')):
    with open(path, encoding='utf-8') as f:
        text = f.read()
    new = text.replace('*', '')
    if new != text:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new)
        print(f"fixed {path}")
print("done")
