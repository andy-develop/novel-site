#!/usr/bin/env python3
"""Scaffold /root/novels/the-white-echo project structure."""
import os, shutil

slug = 'the-white-echo'
base = f'/root/novels/{slug}'
for sub in ['chapters', 'outlines', 'state']:
    os.makedirs(os.path.join(base, sub), exist_ok=True)
print('scaffolded', base)
