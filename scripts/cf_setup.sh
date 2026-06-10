#!/bin/bash
set -e

ACCOUNT_ID='38481ae73b0bdbfbc9b619dc18526041'
TOKEN="$CF_TOKEN"

if [ -z "$TOKEN" ]; then
  echo 'ERROR: set CF_TOKEN env var first'
  exit 1
fi

echo "=== Step 1: 添加域名 lyriq.space 到 Cloudflare ==="
RESP=$(curl -s --header "Authorization: Bearer $TOKEN" \
  --header 'Content-Type: application/json' \
  --data '{"name":"lyriq.space","account":{"id":"38481ae73b0bdbfbc9b619dc18526041"},"jump_start":true}' \
  'https://api.cloudflare.com/client/v4/zones')

echo "$RESP" | python3 -c "
import sys, json
d = json.load(sys.stdin)
if d.get('success'):
    z = d['result']
    print(f'  Zone ID: {z[\"id\"]}')
    print(f'  Status: {z[\"status\"]}')
    ns = z.get('name_servers', [])
    print(f'  Nameservers: {ns}')
    with open('/tmp/cf_zone_id', 'w') as f:
        f.write(z['id'])
    with open('/tmp/cf_nameservers', 'w') as f:
        f.write('\\n'.join(ns))
else:
    print(f'  ERROR: {d.get(\"errors\")}')
    sys.exit(1)
"

echo ""
echo "Done. Zone ID saved to /tmp/cf_zone_id"
echo "Nameservers saved to /tmp/cf_nameservers"