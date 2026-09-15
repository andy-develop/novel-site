import re, glob, os

files = sorted(glob.glob('/root/novels/silly-old-money/chapters/ch[0-9][0-9][0-9].md'))
issues = []
the_count = 0
patterns = set()
for f in files:
    n = int(re.search(r'ch(\d{3})', f).group(1))
    lines = open(f, encoding='utf-8').read().split('\n')
    h1 = lines[0].strip() if lines else ''
    if not h1.startswith('# Chapter '):
        issues.append(f'ch{n:03d}: H1 missing: {h1[:60]!r}')
        continue
    title = h1[2:].strip()
    if not title.startswith(f'Chapter {n}:'):
        issues.append(f'ch{n:03d}: H1 number mismatch: {title[:60]!r}')
    t2 = title[len(f'Chapter {n}:'):].strip()
    if not t2:
        issues.append(f'ch{n:03d}: empty title')
    if re.search(r'[#—–&:()]', t2):
        issues.append(f'ch{n:03d}: bad char in title: {t2!r}')
    if t2.startswith('The '):
        the_count += 1
    if t2 and t2[0].isupper():
        patterns.add('NounPhrase')
    if ',' in t2:
        patterns.add('CommaPhrase')
    if 'II' in t2:
        patterns.add('RomanNumeral')
    # body checks
    for i, ln in enumerate(lines[1:], 2):
        s = ln.strip()
        if s.startswith('#'):
            issues.append(f'ch{n:03d}: hash-leading line {i}: {s[:50]!r}')
        if '*' in s:
            issues.append(f'ch{n:03d}: asterisk line {i}: {s[:50]!r}')
        if re.match(r'^[-—–]{3,}$', s):
            issues.append(f'ch{n:03d}: scene divider line {i}')
    # word count
    wc = len(re.findall(r'\S+', open(f, encoding='utf-8').read()))
    if wc < 1300:
        issues.append(f'ch{n:03d}: too short {wc}')

total = sum(len(re.findall(r'\S+', open(f, encoding='utf-8').read())) for f in files)
print('files:', len(files), 'total words:', total)
print('The-prefixed titles:', the_count, f'({the_count/len(files)*100:.0f}%)')
print('patterns detected:', patterns)
if issues:
    print('ISSUES:')
    for i in issues:
        print(' ', i)
else:
    print('NO ISSUES')
