#!/usr/bin/env python3
"""Check several candidate slugs against R2 books.json."""
import json, os, sys
from botocore.config import Config

def load_dotenv(path):
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"'))

load_dotenv("/root/novel-site/.env")
s3 = boto3 = __import__("boto3")
client = s3.client("s3", endpoint_url=os.environ["R2_ENDPOINT"],
                   aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
                   aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
                   region_name="auto", config=Config(signature_version="s3v4"))
books = json.loads(client.get_object(Bucket=os.environ["R2_BUCKET"], Key="books.json")["Body"].read())
slugs = {b.get("slug") for b in books}
cands = ["the-unclean-spring", "unclean-spring", "the-unsignable", "haven-springs", "brackish",
         "the-brackish-spring", "refused-to-sign", "the-sign-off", "clean-water-only",
         "tessa-vane", "springs-last-stand", "the-fountainhead-spring"]
for s in cands:
    print(s, "TAKEN" if s in slugs else "FREE")
