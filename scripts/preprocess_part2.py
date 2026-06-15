#!/usr/bin/env python3
"""预处理器 - 解析逻辑 (part 2)"""
import json, os, re, sys, yaml
from pathlib import Path

NOVELS_DIR = Path("/root/novels")
OUTPUT_DIR = Path("/root/novel-site/data")

BOOKS = [
    {"id": 1,  "dir": "fulixian",                    "slug": "fulixian"},
    {"id": 2,  "dir": "hulianwang-xiuxian/互联网修仙传", "slug": "hulianwang-xiuxian"},
    {"id": 3,  "dir": "code-epoch",                  "slug": "code-epoch"},
    {"id": 4,  "dir": "delivery-knight",             "slug": "delivery-knight"},
    {"id": 5,  "dir": "moshi-zhuixu",                "slug": "moshi-zhuixu"},
    {"id": 6,  "dir": "daylight-tyrant",             "slug": "daylight-tyrant"},
    {"id": 7,  "dir": "wolf-kings-heart",            "slug": "wolf-kings-heart"},
    {"id": 8,  "dir": "war-god-reborn",              "slug": "war-god-reborn"},
    {"id": 9,  "dir": "apocalypse-romance-system",   "slug": "apocalypse-romance-system"},
    {"id": 10, "dir": "lying-flat-in-the-asylum",    "slug": "lying-flat-in-the-asylum"},
    {"id": 11, "dir": "eldritch-heiress",             "slug": "eldritch-heiress"},
    {"id": 12, "dir": "the-muted",                   "slug": "the-muted"},
    {"id": 13, "dir": "no-thoughts-just-fluff",       "slug": "no-thoughts-just-fluff"},
    {"id": 14, "dir": "delulu-is-the-solulu",         "slug": "delulu-is-the-solulu"},
    {"id": 15, "dir": "Algorithm-A",                   "slug": "algorithm-a"},
    {"id": 16, "dir": "Of-Rust-and-Roses",              "slug": "of-rust-and-roses"},
    {"id": 17, "dir": "Turn-of-the-Screen",             "slug": "turn-of-the-screen"},
    {"id": 18, "dir": "The-Fluidity-of-Us",             "slug": "the-fluidity-of-us"},
    {"id": 19, "dir": "Behind-the-Words",               "slug": "behind-the-words"},
    {"id": 20, "dir": "Glitching-Through-Fate",          "slug": "glitching-through-fate"},
    {"id": 21, "dir": "Phantom-of-the-Deep-Web",          "slug": "phantom-of-the-deep-web"},
    {"id": 22, "dir": "Unraveled",                         "slug": "unraveled"},
    {"id": 23, "dir": "Unfollowed",                        "slug": "unfollowed"},
    {"id": 24, "dir": "ashes-of-us",                       "slug": "ashes-of-us"},
    {"id": 25, "dir": "BurnBook2",                         "slug": "burn-book-2-inferno-exe"},
    {"id": 26, "dir": "Terms-of-Soul",                     "slug": "terms-of-soul"},
    {"id": 27, "dir": "Last-Aurelia",                       "slug": "last-aurelia"},
    {"id": 28, "dir": "GildedGlitch",                       "slug": "gilded-glitch"},
]

# Synonym map: genre text fragments → site standard tags
_SYNONYM_MAP = {
    "Fantasy":      ["fantasy", "dark fantasy", "urban fantasy", "romance fantasy", "werewolf", "litrpg", "eldritch", "vampire", "cozy fantasy", "gothic"],
    "Romance":      ["romance", "monster romance", "stalker romance", "dark romance", "sweet pet", "harem", "love triangle"],
    "Sci-Fi":       ["sci-fi", "scifi", "science fiction", "cyberpunk"],
    "Thriller":     ["thriller", "political thriller", "tech thriller", "cyber thriller", "fashion thriller", "psychological thriller", "cyber-thriller", "psychological horror", "mystery"],
    "Dystopia":     ["dystopia", "dystopian", "post-apocalyptic", "apocalyptic"],
    "Dark Academia":["dark academia"],
    "Contemporary": ["contemporary", "satire", "dark comedy"],
    "Queer":        ["sapphic", "queer", "lgbtq", "gender fluid"],
    "Female Lead":  ["female lead", "female protagonist", "female empowerment"],
}

def _genre_to_tags(genre, data=None):
    """从 YAML genre/subgenre 用近义词匹配出网站标准 tag 列表。"""
    data = data or {}
    meta = data.get("meta", data)
    # 大写 key 兼容 (如 Meta, Premise)
    for key in list(data.keys()):
        if key[0].isupper() and key.lower() not in data:
            data[key.lower()] = data[key]
    # 只读 genre + subgenre(s)
    parts = []
    for key in ["genre", "subgenre"]:
        val = meta.get(key) or data.get(key, "") or meta.get(key + "s") or data.get(key + "s", "")
        if isinstance(val, list):
            parts.extend(str(x) for x in val)
        elif val:
            for sep in [" / ", "/", ", "]:
                val = str(val).replace(sep, "|")
            parts.extend(t.strip() for t in str(val).split("|") if t.strip())
    text = " ".join(parts).lower()
    matched = []
    for tag, synonyms in _SYNONYM_MAP.items():
        for syn in synonyms:
            if syn in text:
                matched.append(tag)
                break
    return sorted(matched)

def parse_yaml(dir_path):
    yp = dir_path / "novel-project.yaml"
    if not yp.exists(): return {}
    with open(yp, "r", encoding="utf-8") as f:
        raw = f.read()
    try:
        data = yaml.safe_load(raw) or {}
    except:
        data = {}
    # 大写 key 兼容 (如 Meta→meta, Premise→premise)
    # 当同时存在大写和小写 key (如 Meta + meta)，合并内容
    for key in list(data.keys()):
        kl = key.lower()
        if key[0].isupper():
            if kl not in data:
                data[kl] = data[key]
            elif isinstance(data[kl], dict) and isinstance(data[key], dict):
                # 大写版优先（通常含更多字段），合并进去
                merged = {**data[kl], **data[key]}
                data[kl] = merged
    meta = data.get("meta", data)
    # meta 存在但可能不含元字段, 回退到顶层
    if not meta.get("title") and not meta.get("name"):
        meta = data
    # 近义词映射：YAML genre 关键词 → 网站标准 tag
    genre = meta.get("genre", "")
    tags = _genre_to_tags(genre, data)

    summary = (data.get("premise", "") or meta.get("premise", "")
               or meta.get("summary", "") or data.get("summary", "")
               or data.get("tagline", "") or meta.get("tagline", "")
               or data.get("synopsis", "") or meta.get("synopsis", ""))
    return {
        "title": meta.get("title") or meta.get("name", dir_path.name),
        "author": meta.get("author", ""),
        "genre": genre,
        "summary": summary,
        "lang": meta.get("language", "chinese"),
        "tags": tags,
    }