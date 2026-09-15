import boto3, json, os
from dotenv import load_dotenv
load_dotenv('/root/novel-site/.env')
s3 = boto3.client('s3', endpoint_url=os.environ['R2_ENDPOINT'],
    aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'], region_name='auto')
bucket = os.environ['R2_BUCKET']
obj = s3.get_object(Bucket=bucket, Key='books.json')
books = json.loads(obj['Body'].read().decode())
ids = [b.get('id') for b in books]
slugs = [b.get('slug') for b in books]
print("max_id:", max(ids) if ids else 0)
print("count:", len(books))
print("slugs:", sorted(slugs))
