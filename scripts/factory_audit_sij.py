import os, re, sys
d = '/root/novels/snow-in-june/chapters'
expected = {
 1:'The Night She Died',2:'Viral',3:"Best Friend's Version",4:'The Takedown',5:'Handcuffs',
 6:'The Letter',7:'What the River Took',8:'Rebirth',9:'Vivian Chase Is Rich',10:'The Comeback',
 11:'White Silk',12:"Dante's Dish",13:'Live Round',14:'Say It on Air',15:"Maya's Confession",
 16:'Why She Lied',17:'The Burn Book',18:'Whistleblower',19:'The Ghost Post',20:'Alex Knows',
 21:"Numbers Don't Lie",22:'Trap Set',23:'Solstice Snow',24:'Face to Face',25:'Proven',
 26:'Reckoning Day',27:'Open Kitchen',28:'Last Snow'}
files = sorted(f for f in os.listdir(d) if re.fullmatch(r'ch\d{3}\.md', f))
total = 0
issues = []
for f in files:
    n = int(re.search(r'(\d+)', f).group(1))
    lines = open(os.path.join(d, f), encoding='utf-8').read().split('\n')
    wc = 0
    h1 = None
    hash_body = []
    aster = 0
    for i, ln in enumerate(lines):
        wc += len(ln.split())
        if i == 0:
            h1 = ln.strip()
        elif ln.startswith('#'):
            hash_body.append(i + 1)
        if '*' in ln:
            aster += 1
    total += wc
    ok = 'OK'
    if h1 != f'# Chapter {n}: {expected.get(n, "???")}':
        ok = f'H1 MISMATCH: {h1!r}'
        issues.append((n, ok))
    if hash_body:
        ok += f' | HASH LINES {hash_body}'
        issues.append((n, f'hash {hash_body}'))
    if aster:
        ok += f' | ASTERISKS {aster}'
        issues.append((n, f'asterisks {aster}'))
    print(f'ch{n:03d} {wc:5d}w {ok}')
print('TOTAL', total)
print('ISSUES', len(issues))
for i in issues:
    print(' ', i)
