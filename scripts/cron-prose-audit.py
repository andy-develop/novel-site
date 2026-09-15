#!/usr/bin/env python3
"""Read-only prose audit: eyes-count, long paragraphs, month/season mentions, key name spellings."""
import os, re, glob

D = '/root/novels/touch-the-veil/chapters'
MONTHS = ['January','February','March','April','May','June','July','August','September','October','November','December',
          'Jan','Feb','Mar','Apr','Jun','Jul','Aug','Sep','Oct','Nov','Dec',
          'winter','spring','summer','autumn','fall']
NAMES = {
 'Elia': r'\bElia\b', 'Dante': r'\bDante\b', 'Augusto': r'\bAugusto\b', 'Marguerite': r'\bMarguerite\b',
 'Nico': r'\bNico\b', 'Sunita': r'\bSunita\b', 'Rafa': r'\bRafa\b', 'Claude': r'\bClaude\b',
 'Ana': r'\bAna\b', 'Leo Moretti': r'\bLeo Moretti\b|Moretti', 'Veil': r'\bVeil\b', 'Aura': r'\bAura\b',
 'cameo': r'\bcameo\b', 'chapel': r'\bchapel\b',
}
MISSPELL = {'Eugenie': 0, 'Margarete': 0, 'Augosto': 0, 'Dantee': 0, 'Sunita ': 0}

for f in sorted(glob.glob(os.path.join(D, 'ch*.md'))):
    name = os.path.basename(f)
    text = open(f, encoding='utf-8').read()
    body = '\n'.join(text.split('\n')[1:])  # drop H1
    eyes = len(re.findall(r'\beyes\b', body, re.I))
    long_paras = []
    for ln in body.split('\n'):
        wc = len(ln.split())
        if wc > 90:
            long_paras.append(wc)
    months = [m for m in MONTHS if re.search(r'\b'+m+r'\b', body)]
    # misspellings
    for bad in MISSPELL:
        if bad.strip() in body:
            MISSPELL[bad] += 1
    flags = []
    if eyes > 3: flags.append(f'eyes={eyes}')
    if long_paras: flags.append(f'long_paras={long_paras[:4]}')
    if months: flags.append('months:' + ','.join(set(months)))
    if flags:
        print(name, ' | '.join(flags))
print('---')
print('MISSPELLINGS:', {k: v for k, v in MISSPELL.items() if v})
# name presence per chapter (all 30)
present = {n: [] for n in NAMES}
for f in sorted(glob.glob(os.path.join(D, 'ch*.md'))):
    num = int(os.path.basename(f)[2:5])
    text = open(f, encoding='utf-8').read()
    for n, pat in NAMES.items():
        if re.search(pat, text):
            present[n].append(num)
for n, chs in present.items():
    missing = [c for c in range(1, 31) if c not in chs]
    print(f'{n}: {len(chs)} chapters; missing: {missing[:12] if missing else "none"}')
