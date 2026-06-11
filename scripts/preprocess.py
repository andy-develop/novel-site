#!/usr/bin/env python3
"""主处理脚本 — 遍历小说, 生成 JSON"""
import json, os, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from preprocess_part2 import NOVELS_DIR, OUTPUT_DIR, BOOKS, parse_yaml
from preprocess_part3 import parse_chapter, get_chapter_files, chapter_id_from_name

def main():
    books_index = []
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for book in BOOKS:
        bid = book["id"]
        slug = book["slug"]
        dir_path = NOVELS_DIR / book["dir"]
        
        meta = parse_yaml(dir_path)
        title = meta.get("title", slug)
        author = meta.get("author", "")
        genre = meta.get("genre", "")
        summary = meta.get("summary", "")
        lang = meta.get("lang", "chinese")

        chapter_files = get_chapter_files(dir_path)
        total_chapters = len(chapter_files)
        print(f"[{bid}] {title} — {total_chapters} 章")

        # 写入 books.json 索引项
        books_index.append({
            "id": bid,
            "slug": slug,
            "title": title,
            "author": author,
            "category": genre,
            "intro": summary[:200] if summary else "",
            "total_chapters": total_chapters,
            "lang": lang,
            "tags": [],
        })

        # 生成 catalog
        catalog_chapters = []
        for f in chapter_files:
            ch_id = chapter_id_from_name(f)
            if ch_id == 0:
                continue
            with open(f, "r", encoding="utf-8") as fh:
                ch_title, paragraphs = parse_chapter(fh.read())
            catalog_chapters.append({"chapter_id": ch_id, "title": ch_title})

        # 写入 catalog
        catalog = {"book_id": bid, "chapters": catalog_chapters}
        cat_path = OUTPUT_DIR / f"catalog_{bid}.json"
        with open(cat_path, "w", encoding="utf-8") as f:
            json.dump(catalog, f, ensure_ascii=False)

        # 生成每章 JSON
        book_dir = OUTPUT_DIR / str(bid)
        book_dir.mkdir(parents=True, exist_ok=True)
        for f in chapter_files:
            ch_id = chapter_id_from_name(f)
            if ch_id == 0:
                continue
            with open(f, "r", encoding="utf-8") as fh:
                ch_title, paragraphs = parse_chapter(fh.read())
            chapter_json = {
                "book_id": bid,
                "chapter_id": ch_id,
                "title": ch_title,
                "content": paragraphs,
            }
            ch_path = book_dir / f"{ch_id}.json"
            with open(ch_path, "w", encoding="utf-8") as fh:
                json.dump(chapter_json, fh, ensure_ascii=False)

    # 写入全局 books.json
    books_path = OUTPUT_DIR / "books.json"
    with open(books_path, "w", encoding="utf-8") as f:
        json.dump(books_index, f, ensure_ascii=False, indent=2)
    
    # 统计
    total_files = sum(1 for p in OUTPUT_DIR.rglob("*.json"))
    total_size = sum(f.stat().st_size for f in OUTPUT_DIR.rglob("*.json"))
    print(f"\n✅ 完成! 共 {len(books_index)} 部小说, {total_files} 个 JSON 文件")
    print(f"总大小: {total_size/1024/1024:.2f} MB")

if __name__ == "__main__":
    main()