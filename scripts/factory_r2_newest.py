#!/usr/bin/env python3
"""Print newest 3 books metadata from R2 books.json (conventions check)."""
import json, boto3

ENV_PATH = "/root/novel-site/.env"
env = {}
with open(ENV_PATH) as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k] = v.strip().strip('"').strip("'")

client = boto3.client(
    "s3",
    endpoint_url=env["R2_ENDPOINT"],
    aws_access_key_id=env["R2_ACCESS_KEY_ID"],
    aws_secret_access_key=env["R2_SECRET_ACCESS_KEY"],
)
obj = client.get_object(Bucket=env["R2_BUCKET"], Key="books.json")
books = json.loads(obj["Body"].read().decode("utf-8"))
books.sort(key=lambda b: b.get("id", 0))
for b in books[-4:]:
    print(json.dumps({k: b.get(k) for k in ("id", "slug", "title", "author", "category", "tags", "lang", "total_chapters")}, ensure_ascii=False))
