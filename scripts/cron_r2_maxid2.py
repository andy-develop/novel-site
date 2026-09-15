import json, boto3
from botocore.config import Config

env = {}
with open('/root/novel-site/.env') as f:
    for line in f:
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            env[k] = v.strip().strip('"').strip("'")

s3 = boto3.client('s3', endpoint_url=env['R2_ENDPOINT'], aws_access_key_id=env['R2_ACCESS_KEY_ID'],
                  aws_secret_access_key=env['R2_SECRET_ACCESS_KEY'], config=Config(signature_version='s3v4'),
                  region_name='auto')
obj = s3.get_object(Bucket=env['R2_BUCKET'], Key='books.json')
books = json.loads(obj['Body'].read().decode())
print('count:', len(books))
print('keys of first:', list(books[0].keys()))
print('sample:', json.dumps(books[0], ensure_ascii=False)[:500])
# find numeric id fields
import collections
for b in books:
    for k, v in b.items():
        if isinstance(v, int) and 100 < v < 10000:
            print('int field:', k, '=', v, '|', b.get('slug'))
            break
