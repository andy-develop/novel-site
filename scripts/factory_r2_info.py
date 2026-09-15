#!/usr/bin/env python3
"""Read books.json from R2: max id, count, existing slugs, langs. Run from /root/novel-site."""
import boto3, json, os
from dotenv import load_dotenv

load_dotenv("/root/novel-site/.env")
s3 = boto3.client(
    "s3",
    endpoint_url=os.environ["R2_ENDPOINT"],
    aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
    region_name="auto",
)
bucket = os.environ["R2_BUCKET"]
obj = s3.get_object(Bucket=bucket, Key="books.json")
books = json.loads(obj["Body"].read().decode("utf-8"))
if isinstance(books, dict):
    books = books.get("books", list(books.values())[0])
ids = [int(b.get("id", 0)) for b in books]
slugs = [b.get("slug", "") for b in books]
langs = {}
for b in books:
    langs[b.get("lang", "?")] = langs.get(b.get("lang", "?"), 0) + 1
print("total_books:", len(books))
print("max_id:", max(ids) if ids else 0)
print("langs:", langs)
print("slugs:")
for s in sorted(slugs):
    print(" ", s)
