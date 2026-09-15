#!/usr/bin/env python3
"""Verify R2 state for tomorrow-girl (id 1518). Cron-safe."""
import json, sys
sys.path.insert(0, "/root/novel-site")
try:
    from dotenv import load_dotenv
    load_dotenv("/root/novel-site/.env")
except Exception:
    pass
import os, boto3
from botocore.config import Config

s3 = boto3.client("s3", endpoint_url=os.environ.get("R2_ENDPOINT"),
                  aws_access_key_id=os.environ.get("R2_ACCESS_KEY_ID"),
                  aws_secret_access_key=os.environ.get("R2_SECRET_ACCESS_KEY"),
                  config=Config(signature_version="s3v4"), region_name="auto")
B = os.environ.get("R2_BUCKET") or "novel-data"

books = json.loads(s3.get_object(Bucket=B, Key="books.json")["Body"].read())
entry = [b for b in books if b.get("slug") == "tomorrow-girl"]
print("books.json entry:", json.dumps(entry[0] if entry else "MISSING", ensure_ascii=False)[:300])

cat = json.loads(s3.get_object(Bucket=B, Key="catalog_1518.json")["Body"].read())
print("catalog chapters:", len(cat["chapters"]), "| ids int:", all(isinstance(c["chapter_id"], int) for c in cat["chapters"]))

ch1 = json.loads(s3.get_object(Bucket=B, Key="1518/1.json")["Body"].read())
print("ch1 keys:", list(ch1.keys()))
print("ch1 title:", ch1.get("title"))
print("ch1 highlight:", (ch1.get("highlight") or "")[:80])
print("ch1 content paras:", len(ch1.get("content") or []))
print("ch1 content words:", len(" ".join(ch1.get("content") or []).split()))
ch28 = json.loads(s3.get_object(Bucket=B, Key="1518/28.json")["Body"].read())
print("ch28 title:", ch28.get("title"), "| highlight:", (ch28.get("highlight") or "")[:60])
