#!/usr/bin/env python3
"""Phase 1: sample 4 candidate pairs with timestamp seed."""
import random, sys

titles = [l.strip() for l in open('/tmp/classics.txt', encoding='utf-8') if l.strip()]
seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1788901247
random.seed(seed)
picked = random.sample(titles, 8)
for i in range(0, 8, 2):
    print(f"PAIR{i//2+1}: 《{picked[i]}》 x 《{picked[i+1]}》")
