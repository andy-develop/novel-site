#!/usr/bin/env python3
"""Query R2 books.json: max id, existing slugs, total books."""
import json
import os
import boto3
from botocore.config import Config

ENV = "/root/novel-site/.env"
def load_dotenv(path):
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"'))

load_dotenv(ENV)

s3 = boto3.client(
    "s3",
    endpoint_url=os.environ["R2_ENDPOINT"],
    aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
    region_name="auto",
    config=Config(signature_version="s3v4"),
)
bucket = os.environ["R2_BUCKET"]
obj = s3.get_object(Bucket=bucket, Key="books.json")
books = json.loads(obj["Body"].read().decode("utf-8"))
ids = [b.get("id") for b in books if isinstance(b.get("id"), int)]
max_id = max(ids) if ids else 0
slugs = sorted(b.get("slug", "") for b in books)
print("MAX_ID:", max_id)
print("BOOK_COUNT:", len(books))
print("SLUGS:", ",".join(slugs))
