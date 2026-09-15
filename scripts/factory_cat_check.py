#!/usr/bin/env python3
"""Sample category values from R2 books.json."""
import json, os, boto3
from collections import Counter

ENV_PATH = "/root/novel-site/.env"
env = {}
with open(ENV_PATH) as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k] = v.strip().strip('"').strip("'")

client = boto3.client("s3", endpoint_url=env["R2_ENDPOINT"],
    aws_access_key_id=env["R2_ACCESS_KEY_ID"], aws_secret_access_key=env["R2_SECRET_ACCESS_KEY"])
books = json.loads(client.get_object(Bucket=env["R2_BUCKET"], Key="books.json")["Body"].read().decode("utf-8"))
cats = Counter(b.get("category", "") for b in books)
print("top categories:", cats.most_common(12))
recent = sorted(books, key=lambda b: b.get("id", 0))[-8:]
for b in recent:
    print(b.get("id"), "|", b.get("slug"), "|", b.get("category"), "|", b.get("lang"), "|", b.get("total_chapters"))
