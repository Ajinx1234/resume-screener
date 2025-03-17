import boto3
import os
from dotenv import load_dotenv

# Load AWS credentials from .env file
load_dotenv()

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

# Debugging print statements
print("AWS_ACCESS_KEY:", AWS_ACCESS_KEY)
print("AWS_SECRET_KEY:", AWS_SECRET_KEY)
print("S3_BUCKET_NAME:", BUCKET_NAME)

if not AWS_ACCESS_KEY or not AWS_SECRET_KEY or not BUCKET_NAME:
    print("❌ AWS credentials or bucket name missing! Check your .env file.")
    exit()

# Initialize S3 client
s3 = boto3.client("s3", aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)

def upload_resume(file_path, file_name):
    """Uploads a resume to AWS S3"""
    try:
        s3.upload_file(file_path, BUCKET_NAME, file_name)
        print(f"✅ Uploaded {file_name} to {BUCKET_NAME}")
    except Exception as e:
        print(f"❌ Upload failed: {e}")

# Test the function
if __name__ == "__main__":
    upload_resume("test_resume.pdf", "resume1.pdf")
