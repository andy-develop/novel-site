#!/usr/bin/env python3
"""Split overly long paragraphs (>600 chars) at sentence boundaries."""
import re

targets = {
    'ch010.md': [99],
    'ch023.md': [55],
    'ch024.md': [17],
    'ch028.md': [65],
}

def split_para(text, maxlen=430):
    sents = re.split(r'(?<=[.!?])\s+', text.strip())
    chunks, cur = [], ''
    for s in sents:
        if len(cur) + len(s) + 1 > maxlen and cur:
            chunks.append(cur)
            cur = s
        else:
            cur = (cur + ' ' + s).strip() if cur else s
    if cur:
        chunks.append(cur)
    return '\n'.join(chunks)

for fname, lines in targets.items():
    path = f'/root/novels/vanity-pilgrim/chapters/{fname}'
    with open(path, encoding='utf-8') as f:
        lines_out = f.readlines()
    for ln in lines:
        idx = ln - 1
        orig = lines_out[idx].rstrip('\n')
        new = split_para(orig)
        if '\n' in new:
            lines_out[idx] = new + '\n'
            print(f'{fname}:{ln} split {len(orig)} chars -> {len(new)} chars')
        else:
            print(f'{fname}:{ln} unchanged ({len(orig)} chars)')
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(lines_out)
