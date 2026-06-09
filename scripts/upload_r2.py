#!/usr/bin/env python3
"""R2 上传脚本 — 将章节数据上传到 Cloudflare R2

用法:
  # 设置环境变量
  export R2_ACCESS_KEY_ID=your_key
  export R2_SECRET_ACCESS_KEY=your_secret
  export R2_ENDPOINT=https://<accountid>.r2.cloudflarestorage.com
  export R2_BUCKET=novel-data
  export R2_PUBLIC_URL=https://data.yourdomain.com

  # 上传所有章节数据
  python3 scripts/upload_r2.py
"""
import json, os, sys, boto3
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# R2 配置
ACCESS_KEY = os.environ.get("R2_ACCESS_KEY_ID")
SECRET_KEY = os.environ.get("R2_SECRET_ACCESS_KEY")
ENDPOINT = os.environ.get("R2_ENDPOINT")
BUCKET = os.environ.get("R2_BUCKET", "novel-data")

if not ACCESS_KEY or not SECRET_KEY or not ENDPOINT:
    print("❌ 请设置环境变量:")
    print("   export R2_ACCESS_KEY_ID=...")
    print("   export R2_SECRET_ACCESS_KEY=...")
    print("   export R2_ENDPOINT=https://<accountid>.r2.cloudflarestorage.com")
    sys.exit(1)

# S3 兼容客户端
client = boto3.client(
    "s3",
    endpoint_url=ENDPOINT,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
)

def upload_file(filepath: Path):
    """上传一个 JSON 文件到 R2, 设置 Cache-Control 一年"""
    key = str(filepath.relative_to(DATA_DIR))
    content_type = "application/json"
    
    # 书本目录 和 章节内容 → 缓存一年（死数据）
    # books.json 也缓存一年
    cache_control = "public, max-age=31536000, immutable"
    
    try:
        with open(filepath, "rb") as f:
            client.put_object(
                Bucket=BUCKET,
                Key=key,
                Body=f,
                ContentType=content_type,
                CacheControl=cache_control,
            )
        return True, key
    except Exception as e:
        return False, f"{key}: {e}"

def main():
    # 收集所有 JSON 文件
    files = list(DATA_DIR.rglob("*.json"))
    print(f"📦 共 {len(files)} 个文件待上传到 R2 bucket '{BUCKET}'")
    
    # 排除 books.json — 它在 GitHub Pages 仓库里
    files = [f for f in files if f.name != "books.json"]
    print(f"📤 上传 {len(files)} 个文件 (books.json 留在 GitHub Pages)")
    
    success = 0
    fail = 0
    
    with ThreadPoolExecutor(max_workers=20) as pool:
        futures = {pool.submit(upload_file, f): f for f in files}
        for future in as_completed(futures):
            ok, msg = future.result()
            if ok:
                success += 1
                print(f"  ✓ {msg}")
            else:
                fail += 1
                print(f"  ✗ {msg}")
    
    print(f"\n✅ 完成! 成功: {success}, 失败: {fail}")
    
    if success:
        print(f"\n🔗 确保你的 R2 绑定了自定义域名:")
        print(f"   上传位置: {ENDPOINT}/{BUCKET}/")
        print(f"   前端配置: R2_BASE = https://data.yourdomain.com")

if __name__ == "__main__":
    main()