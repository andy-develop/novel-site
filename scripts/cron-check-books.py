import json, boto3, os
from dotenv import load_dotenv
load_dotenv('/root/novel-site/.env')
s3 = boto3.client('s3', endpoint_url=os.environ['R2_ENDPOINT'],
                  aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
                  aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'],
                  region_name='auto')
resp = s3.get_object(Bucket=os.environ['R2_BUCKET'], Key='books.json')
books = json.loads(resp['Body'].read())
ids = sorted(b['id'] for b in books)
print("count:", len(books))
print("max_id:", max(ids))
for b in sorted(books, key=lambda x: x['id'])[-6:]:
    print(b['id'], b.get('slug'), b.get('lang'), b.get('total_chapters'), b.get('title','')[:40])
slugs = [b.get('slug') for b in books]
print("SLUGS:", slugs)
