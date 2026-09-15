#!/usr/bin/env python3
"""Pick 4 candidate classic pairs with random seed, print for LLM scoring."""
import random, re, sys, json

SRC = '/root/世界名著大全.md'

def load_classics():
    titles = []
    with open(SRC, encoding='utf-8') as f:
        for line in f:
            m = re.search(r'《([^》]+)》', line)
            if m:
                t = m.group(1).strip()
                author = line.split('|')[-1].strip() if '|' in line else ''
                titles.append((t, author))
    return titles

def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1789333259
    n_pairs = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    classics = load_classics()
    # dedupe titles
    seen = set()
    uniq = []
    for t, a in classics:
        if t not in seen:
            seen.add(t)
            uniq.append((t, a))
    rng = random.Random(seed)
    # sample 8 distinct titles, pair them off
    idx = rng.sample(range(len(uniq)), min(2 * n_pairs, len(uniq)))
    pairs = []
    for i in range(0, len(idx) - 1, 2):
        pairs.append((uniq[idx[i]], uniq[idx[i+1]]))
    out = []
    for p in pairs:
        out.append({'a': p[0][0], 'a_author': p[0][1], 'b': p[1][0], 'b_author': p[1][1]})
    print(json.dumps(out, ensure_ascii=False, indent=1))

if __name__ == '__main__':
    main()
