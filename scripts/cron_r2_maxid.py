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
ids = [b.get('book_id') for b in books if isinstance(b.get('book_id'), int)]
print('count:', len(books))
print('max_id:', max(ids) if ids else 0)
for b in sorted(books, key=lambda x: x.get('book_id', 0))[-8:]:
    print(b.get('book_id'), '|', b.get('slug'), '|', b.get('title'), '|', b.get('lang'), '| chapters:', b.get('total_chapters'))
