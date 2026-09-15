#!/usr/bin/env python3
"""Read R2 books.json: max id, slug list, latest entries."""
import json
import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv("/root/novel-site/.env")
except Exception:
    pass

import boto3
from botocore.config import Config

endpoint = os.environ["R2_ENDPOINT"]
bucket = os.environ["R2_BUCKET"]
key_id = os.environ["R2_ACCESS_KEY_ID"]
secret = os.environ["R2_SECRET_ACCESS_KEY"]

s3 = boto3.client(
    "s3",
    endpoint_url=endpoint,
    aws_access_key_id=key_id,
    aws_secret_access_key=secret,
    config=Config(signature_version="s3v4"),
)

obj = s3.get_object(Bucket=bucket, Key="books.json")
books = json.loads(obj["Body"].read().decode("utf-8"))
if isinstance(books, dict):
    books = books.get("books", books)
ids = [b.get("id") for b in books if isinstance(b, dict)]
print("count:", len(books))
print("max_id:", max(ids) if ids else 0)
slugs = sorted(b.get("slug", "") for b in books if isinstance(b, dict))
print("slugs:", ",".join(slugs))
print("--- latest 8 ---")
for b in sorted(books, key=lambda x: x.get("id", 0), reverse=True)[:8]:
    print(b.get("id"), "|", b.get("slug"), "|", b.get("lang"), "|", b.get("total_chapters"), "|", b.get("title"))
