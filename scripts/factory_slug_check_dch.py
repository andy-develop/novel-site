#!/usr/bin/env python3
"""Check slug + id availability in R2 books.json for dragon-carved-heart."""
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
slugs = set(b.get("slug", "") for b in books)
ids = [b.get("id") for b in books]
target = "dragon-carved-heart"
print("slug_taken:", target in slugs)
print("next_id:", max(ids) + 1)
print("id_1480_taken:", 1480 in ids)
for b in books:
    if b.get("slug") == target:
        print("EXISTING ENTRY:", json.dumps(b, ensure_ascii=False)[:400])
