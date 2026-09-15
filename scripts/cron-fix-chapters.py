#!/usr/bin/env python3
"""Fix pass: ch018 season consistency, eyes overuse trims, long-paragraph splits."""
import re, os

D = '/root/novels/touch-the-veil/chapters'

EYES = {
 'ch021.md': [
   ("His eyes sweep the press pit and come back, and he knows her.",
    "His gaze sweeps the press pit and comes back, and he knows her."),
   ("and his eyes say what his mouth cannot.",
    "and the way he looks at her says what his mouth cannot."),
   ("Their eyes meet across the room.", "Their gazes meet across the room."),
   ("Her eyes never leave the terminal.", "Her gaze never leaves the terminal."),
   ("and Marguerite's eyes go flat", "and Marguerite's gaze goes flat"),
   ("the smile has gone out of his eyes", "the smile has gone out of his face"),
   ("at the ruin behind his eyes", "at the ruin behind his gaze"),
 ],
 'ch017.md': [
   ("His eyes are flat.", "His gaze is flat."),
   ("she can feel his eyes on her back", "she can feel his gaze on her back"),
   ("He meets her eyes.", "He meets her gaze."),
   ("He finally meets her eyes.", "He finally meets her gaze."),
 ],
 'ch022.md': [
   ("a flicker in her eyes", "a flicker in her gaze"),
   ("but her eyes do. They go flat", "but her gaze does. It goes flat"),
   ("but his eyes are not.", "but his gaze is not."),
 ],
 'ch028.md': [
   ("Her eyes leave the roaring room and find the back of the hall",
    "Her gaze leaves the roaring room and finds the back of the hall"),
   ("Their eyes meet across the whole length of the hall",
    "Their gazes meet across the whole length of the hall"),
   ("her eyes fixed on the back of the hall", "her gaze fixed on the back of the hall"),
 ],
}

SEASON = ('the winter of 2011', 'the summer of 2011')

def split_paragraph(line):
    """Split a long paragraph at the sentence boundary nearest the middle."""
    n = len(line)
    # sentence end positions: . " ? ! followed by space (or end), then non-lowercase
    ends = []
    for m in re.finditer(r'(?<=[.!"?])[\s]+(?=[A-Z"\u201c])', line):
        ends.append(m.end())
    if not ends:
        return None
    target = n * 0.55
    best = min(ends, key=lambda e: abs(e - target))
    if best < n * 0.35 or best > n * 0.75:
        return None
    return line[:best].rstrip() + '\n' + line[best:].lstrip()

changed = []
for fname, subs in EYES.items():
    path = os.path.join(D, fname)
    text = open(path, encoding='utf-8').read()
    for old, new in subs:
        if old in text:
            text = text.replace(old, new)
            changed.append(f'{fname}: eyes-fix')
        else:
            changed.append(f'{fname}: MISSING {old[:40]!r}')
    open(path, 'w', encoding='utf-8').write(text)

# season fix
p = os.path.join(D, 'ch018.md')
t = open(p, encoding='utf-8').read()
if SEASON[0] in t:
    t = t.replace(*SEASON)
    open(p, 'w', encoding='utf-8').write(t)
    changed.append('ch018.md: winter->summer 2011')
else:
    changed.append('ch018.md: season string not found')

# long paragraph splits (>400 chars)
for fname in sorted(os.listdir(D)):
    if not fname.endswith('.md'):
        continue
    path = os.path.join(D, fname)
    lines = open(path, encoding='utf-8').read().split('\n')
    out = []
    for ln in lines:
        if len(ln) > 400:
            split = split_paragraph(ln)
            if split:
                out.extend(split.split('\n'))
                changed.append(f'{fname}: split ({len(ln.split())}w)')
            else:
                out.append(ln)
        else:
            out.append(ln)
    open(path, 'w', encoding='utf-8').write('\n'.join(out))

print('CHANGES', len(changed))
for c in changed:
    print('  ', c)
