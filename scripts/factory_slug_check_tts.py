#!/usr/bin/env python3
"""Check the-truth-sickness slug + nearby variants against R2 books.json."""
import json, os
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
import boto3
client = boto3.client("s3", endpoint_url=os.environ["R2_ENDPOINT"],
                      aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
                      aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
                      region_name="auto", config=Config(signature_version="s3v4"))
books = json.loads(client.get_object(Bucket=os.environ["R2_BUCKET"], Key="books.json")["Body"].read())
slugs = {b.get("slug") for b in books}
for s in ["the-truth-sickness", "truth-sickness", "the-orchard", "orchard", "mila-chen",
          "the-perfect-defect", "perfect-defect", "the-first-honest-thing"]:
    print(s, "TAKEN" if s in slugs else "FREE")
