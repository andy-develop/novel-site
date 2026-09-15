#!/usr/bin/env python3
"""Recon R2: max book id + existing slugs (avoid collision)."""
import os, json, boto3

def load_env(path):
    env = {}
    for line in open(path):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env

env = load_env("/root/novel-site/.env")
client = boto3.client("s3", endpoint_url=env["R2_ENDPOINT"],
                      aws_access_key_id=env["R2_ACCESS_KEY_ID"],
                      aws_secret_access_key=env["R2_SECRET_ACCESS_KEY"])
obj = client.get_object(Bucket=env["R2_BUCKET"], Key="books.json")
books = json.loads(obj["Body"].read().decode("utf-8"))
ids = [b["id"] for b in books]
maxid = max(ids)
slugs = set(b.get("slug") for b in books)
print(f"total books: {len(books)}  max id: {maxid}")
print("slugs:", " ".join(sorted(slugs)))
