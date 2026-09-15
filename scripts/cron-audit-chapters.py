#!/usr/bin/env python3
"""Audit chapters: H1 contract, word counts, hash lines, title special chars."""
import re, os, sys

d = '/root/novels/the-golden-boy-is-dead/chapters'
files = sorted(f for f in os.listdir(d) if re.fullmatch(r'ch\d{3}\.md', f))
print(f"{len(files)} files")
expected = {
 1:"Seven Strangers, One Corpse",2:"Rule Number One",3:"She Screamed",
 4:"Everybody Loves a Graveyard",5:"I Knew Him When",6:"Cabin on Tahoe",
 7:"What Danny Gave Dax",8:"Night Before",9:"Founderless",10:"Fine Print",
 11:"Exit Row",12:"Kindness Tale",13:"Aunt Connie's Version",14:"Enforcer's Day",
 15:"Day Five",16:"Patron's Tale",17:"Old Place",18:"Second Note",
 19:"Lake's Version",20:"All the Receipts",21:"Don't Drink the Lemonade",
 22:"Trial by Feed",23:"Price of a Verse",24:"What Connie Kept",
 25:"Financier's Confession",26:"Live Chat",27:"Verdict",28:"Finish Line",
 29:"Eighth Tale",30:"What the Water Kept"}
total = 0
bad_h1 = []
hash_body = []
thin = []
titles = []
for f in files:
    n = int(f[2:5])
    path = os.path.join(d, f)
    lines = open(path, encoding='utf-8').read().split('\n')
    h1 = lines[0].strip() if lines else ''
    words = len(re.findall(r"[A-Za-z0-9']+", ' '.join(lines)))
    total += words
    want = f"# Chapter {n}: {expected.get(n, '?')}"
    if h1 != want:
        bad_h1.append((f, h1[:70], want[:70]))
    for i, ln in enumerate(lines[1:], 2):
        if ln.startswith('#'):
            hash_body.append((f, i, ln[:50]))
    # special chars in title
    t = h1.replace(f"Chapter {n}:", '').strip() if h1.startswith('#') else h1
    titles.append(t)
    if words < 1600:
        thin.append((f, words))
    if words < 1300:
        thin.append((f, words, "BELOW HARD FLOOR"))
print(f"TOTAL WORDS: {total}")
print(f"AVG: {total // len(files)}")
print("THIN (<1600):", thin)
print("BAD H1:")
for x in bad_h1: print("  ", x)
print("HASH BODY LINES:")
for x in hash_body: print("  ", x)
# title pattern check
the_start = sum(1 for t in titles if t.startswith('The '))
print(f"'The ' starters: {the_start}/{len(titles)}")
for t in titles:
    if re.search(r'[#—–&:()]', t):
        print("SPECIAL CHAR TITLE:", t)
