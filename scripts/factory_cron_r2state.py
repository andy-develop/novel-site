#!/usr/bin/env python3
"""Read R2 books.json: max id, existing slugs, last few entries."""
import boto3, json, os
from dotenv import load_dotenv

load_dotenv("/root/novel-site/.env")
s3 = boto3.client(
    "s3",
    endpoint_url=os.environ["R2_ENDPOINT"],
    aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
)
obj = s3.get_object(Bucket=os.environ["R2_BUCKET"], Key="books.json")
books = json.loads(obj["Body"].read())
ids = [b.get("id") for b in books]
slugs = [b.get("slug") for b in books]
print(f"total books: {len(books)}")
print(f"max id: {max(ids)}")
print(f"ids range: {min(ids)}..{max(ids)}")
print("existing slugs:", ", ".join(slugs[-25:]))
print("---last 3 entries---")
for b in books[-3:]:
    print(json.dumps({k: b.get(k) for k in ("id", "slug", "title", "lang", "total_chapters")}, ensure_ascii=False))
