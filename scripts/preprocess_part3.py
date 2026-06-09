def parse_chapter(content):
    """解析 .md 章节, 返回 (title, paragraphs)"""
    lines = content.split("\n")
    title = ""
    paragraphs = []
    buf = []
    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
            continue
        stripped = line.strip()
        if not stripped:
            if buf:
                paragraphs.append("\n".join(buf).strip())
                buf = []
            continue
        if stripped == "---":
            continue
        buf.append(stripped)
    if buf:
        paragraphs.append("\n".join(buf).strip())
    return title, paragraphs


def get_chapter_files(dir_path):
    """获取小说章节文件列表（按 ch001.md 排序）"""
    ch_dir = dir_path / "chapters"
    if not ch_dir.exists():
        return []
    files = sorted(ch_dir.glob("ch*.md"))
    return files


import re

def chapter_id_from_name(fname):
    """从文件名提取章节号: ch001.md -> 1"""
    m = re.search(r"ch(\d+)", fname.stem)
    if m:
        return int(m.group(1))
    return 0