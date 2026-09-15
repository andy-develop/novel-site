#!/usr/bin/env python3
"""Query R2 novel-data books.json: max id, existing slugs, latest books."""
import json, boto3
from dotenv import load_dotenv
import os

load_dotenv("/root/novel-site/.env")

s3 = boto3.client(
    "s3",
    endpoint_url=os.environ["R2_ENDPOINT"],
    aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
    region_name="auto",
)

obj = s3.get_object(Bucket=os.environ["R2_BUCKET"], Key="books.json")
books = json.loads(obj["Body"].read().decode("utf-8"))

ids = [b.get("id") for b in books if isinstance(b.get("id"), int)]
max_id = max(ids) if ids else 0
slugs = [b.get("slug") for b in books if b.get("slug")]

print(f"total books: {len(books)}")
print(f"max id: {max_id}")
print(f"next id: {max_id + 1}")
print("slugs:")
for s in sorted(slugs):
    print(s)
