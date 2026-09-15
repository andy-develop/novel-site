#!/usr/bin/env python3
"""Fix pass 2: ch009 February->January, eyes trims in ch006/ch009."""
import os

D = '/root/novels/touch-the-veil/chapters'

FIXES = {
 'ch006.md': [
   ("something in his eyes she has never seen before",
    "something in his gaze she has never seen before"),
   ("His eyes come back to the serial number.",
    "His gaze comes back to the serial number."),
 ],
 'ch009.md': [
   ("the thing that happened on a roof in February",
    "the thing that happened on a roof in January"),
   ("the fountain is still frozen from February",
    "the fountain is still frozen from January"),
   ("His eyes find Elia across the crowd.",
    "His gaze finds Elia across the crowd."),
   ("Marguerite's eyes flick to Elia's throat",
    "Marguerite's gaze flicks to Elia's throat"),
   ("their eyes meet over the heads of the crowd",
    "their gazes meet over the heads of the crowd"),
   ("She has felt his eyes on her all night",
    "She has felt his gaze on her all night"),
 ],
}

for fname, subs in FIXES.items():
    path = os.path.join(D, fname)
    text = open(path, encoding='utf-8').read()
    for old, new in subs:
        if old in text:
            text = text.replace(old, new)
            print('OK', fname, old[:40])
        else:
            print('MISS', fname, old[:50])
    open(path, 'w', encoding='utf-8').write(text)
