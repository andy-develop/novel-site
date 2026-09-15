#!/usr/bin/env python3
"""Read R2 books.json, print max id + all existing slugs (for collision check)."""
import json, os, boto3

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
ids = [b.get("id") for b in books]
print("total_books:", len(books))
print("max_id:", max(ids))
print("slugs:", ",".join(sorted(b.get("slug", "") for b in books)))
