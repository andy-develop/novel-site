#!/usr/bin/env python3
"""Cloudflare 自动设置: 添加域名 + 创建 R2 Bucket + 绑定域名 + CORS"""
import json, os, sys, urllib.request, urllib.error

with open('/tmp/cf_token.txt') as f:
    TOKEN = f.read().strip()
if not TOKEN:
    print('ERROR: token not configured')
    sys.exit(1)

ACCOUNT_ID = '38481ae73b0bdbfbc9b619dc18526041'
BASE = 'https://api.cloudflare.com/client/v4'

def cf_api(method, path, data=None):
    url = BASE + path
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/json',
    }
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        err = e.read().decode()
        print(f'HTTP {e.code}: {err}')
        return json.loads(err) if err else {'success': False, 'errors': [{'message': str(e)}]}

# Step 1: Add zone
def add_zone():
    print('=== Step 1: 添加域名 lyriq.space ===')
    data = {
        'name': 'lyriq.space',
        'account': {'id': ACCOUNT_ID},
        'jump_start': True,
    }
    result = cf_api('POST', '/zones', data)
    if result.get('success'):
        z = result['result']
        print(f'  Zone ID: {z["id"]}')
        print(f'  Status: {z["status"]}')
        print(f'  Nameservers: {z["name_servers"]}')
        with open('/tmp/cf_zone_id', 'w') as f:
            f.write(z['id'])
        with open('/tmp/cf_nameservers', 'w') as f:
            f.write('\n'.join(z['name_servers']))
        return z['id']
    else:
        errs = result.get('errors', [])
        # 可能已经存在
        if any(e.get('code') == 10056 for e in errs):
            print('  域名已在 Cloudflare 中, 查询现有 Zone ID...')
            zones = cf_api('GET', '/zones?name=lyriq.space')
            if zones.get('success') and zones['result']:
                z = zones['result'][0]
                print(f'  Zone ID: {z["id"]}')
                print(f'  Status: {z["status"]}')
                print(f'  Nameservers: {z["name_servers"]}')
                with open('/tmp/cf_zone_id', 'w') as f:
                    f.write(z['id'])
                with open('/tmp/cf_nameservers', 'w') as f:
                    f.write('\n'.join(z['name_servers']))
                return z['id']
        for e in errs:
            print(f'  ERROR: {e}')
        return None

add_zone()