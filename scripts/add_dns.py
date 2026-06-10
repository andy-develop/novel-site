#!/usr/bin/env python3
"""Add DNS A records for lyriq.space -> GitHub Pages"""
import json, urllib.request, os

TOKEN = os.environ.get("CF_TOKEN", "")
if not TOKEN:
    print("CF_TOKEN env var required")
    exit(1)

ZONE_ID = "91359e58f51796edc4913b579a8500b5"
BASE = f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records"

ips = ["185.199.108.153", "185.199.109.153", "185.199.110.153", "185.199.111.153"]

for ip in ips:
    body = json.dumps({"type":"A","name":"lyriq.space","content":ip,"ttl":1,"proxied":True}).encode()
    req = urllib.request.Request(BASE, data=body,
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
        method="POST")
    try:
        resp = json.loads(urllib.request.urlopen(req).read())
        print(f"{ip} -> lyriq.space {'OK' if resp['success'] else 'FAIL'}: {resp.get('errors', '')}")
    except Exception as e:
        print(f"{ip} -> FAIL: {e}")
