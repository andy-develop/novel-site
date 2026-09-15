#!/usr/bin/env python3
"""Fix ch024 highlight on R2 (strip meta prefix + stray quote)."""
import json, boto3

env = {}
with open("/root/novel-site/.env") as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k] = v.strip().strip('"').strip("'")

c = boto3.client(
    "s3",
    endpoint_url=env["R2_ENDPOINT"],
    aws_access_key_id=env["R2_ACCESS_KEY_ID"],
    aws_secret_access_key=env["R2_SECRET_ACCESS_KEY"],
)
bucket = env["R2_BUCKET"]
key = "1489/24.json"
obj = json.loads(c.get_object(Bucket=bucket, Key=key)["Body"].read())
obj["highlight"] = "Watching June get dragged to the van, Mira runs before she even decides to move."
c.put_object(
    Bucket=bucket,
    Key=key,
    Body=json.dumps(obj, ensure_ascii=False).encode(),
    ContentType="application/json",
    CacheControl="public, max-age=31536000, immutable",
)
chk = json.loads(c.get_object(Bucket=bucket, Key=key)["Body"].read())
print("new highlight:", chk["highlight"])
assert chk["highlight"].startswith("Watching June")
print("FIX OK")
