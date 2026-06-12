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
]

def parse_yaml(dir_path):
    yp = dir_path / "novel-project.yaml"
    if not yp.exists(): return {}
    with open(yp, "r", encoding="utf-8") as f:
        raw = f.read()
    try:
        data = yaml.safe_load(raw) or {}
    except:
        data = {}
    meta = data.get("meta", data)
    # meta 存在但可能不含元字段, 回退到顶层
    if not meta.get("title") and not meta.get("name"):
        meta = data
    return {
        "title": meta.get("title") or meta.get("name", dir_path.name),
        "author": meta.get("author", ""),
        "genre": meta.get("genre", ""),
        "summary": data.get("premise", "") or meta.get("summary", ""),
        "lang": meta.get("language", "chinese"),
    }