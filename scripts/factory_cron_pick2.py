#!/usr/bin/env python3
"""Cron factory: sample classic pairs with timestamp seed."""
import re, random, sys, time

seed = int(time.time())
text = open('/root/世界名著大全.md', encoding='utf-8').read()
titles = re.findall(r'《([^》]+)》', text)
titles = list(dict.fromkeys(titles))  # dedupe, keep order
print("SEED:", seed)
print("TITLES:", len(titles))

random.seed(seed)
for i in range(4):
    pair = random.sample(titles, 2)
    print(f"PAIR{i+1}: {pair[0]} || {pair[1]}")
