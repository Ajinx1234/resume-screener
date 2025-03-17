import boto3
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")  # ✅ Set a default region
BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
TEXT_BUCKET_NAME = os.getenv("S3_EXTRACTED_TEXT_BUCKET")

# ✅ Fix: Specify `region_name`
textract_client = boto3.client(
    "textract",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION  # ✅ Added this line
)

def extract_text_from_s3(file_name):
    """Extracts text from an S3 file using AWS Textract."""
    response = textract_client.start_document_text_detection(
        DocumentLocation={"S3Object": {"Bucket": BUCKET_NAME, "Name": file_name}}
    )
    job_id = response["JobId"]

    for _ in range(60):  # Wait for max 60 seconds
        time.sleep(2)
        result = textract_client.get_document_text_detection(JobId=job_id)
        if result["JobStatus"] == "SUCCEEDED":
            text = "\n".join([block["Text"] for block in result.get("Blocks", []) if block["BlockType"] == "LINE"])
            os.makedirs("tmp", exist_ok=True)  # ✅ Ensure the 'tmp' directory exists
            with open(f"tmp/{os.path.splitext(file_name)[0]}.txt", "w", encoding="utf-8") as f:
                f.write(text)
            return text
    return None

if __name__ == "__main__":
    import sys
    extract_text_from_s3(sys.argv[1])
