import json
import time
import boto3
from botocore.client import Config

s3 = boto3.client(
    "s3",
    endpoint_url="http://object-storage-server:9000",
    aws_access_key_id="minioadmin",
    aws_secret_access_key="minioadmin",
    config=Config(signature_version="s3v4"),
    region_name="us-east-1",
)

for _ in range(30):
    try:
        s3.list_buckets()
        break
    except Exception:
        time.sleep(2)

for bucket in ["demo", "profile-pics", "documents"]:
    try:
        s3.create_bucket(Bucket=bucket)
    except Exception:
        pass
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"AWS": ["*"]},
                "Action": ["s3:GetObject"],
                "Resource": [f"arn:aws:s3:::{bucket}/*"],
            }
        ],
    }
    s3.put_bucket_policy(Bucket=bucket, Policy=json.dumps(policy))

s3.upload_file("/seed-web/index.html", "demo", "index.html", ExtraArgs={"ContentType": "text/html"})
s3.upload_file("/seed/avatar.jpg", "profile-pics", "avatar.jpg", ExtraArgs={"ContentType": "image/jpeg"})
s3.upload_file("/seed/BaoCao.pdf", "documents", "BaoCao.pdf", ExtraArgs={"ContentType": "application/pdf"})
s3.upload_file("/seed/BaoCao.pdf", "documents", "report.pdf", ExtraArgs={"ContentType": "application/pdf"})
print("MinIO init done: demo/index.html, profile-pics/avatar.jpg, documents/BaoCao.pdf, documents/report.pdf")
