from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import boto3
import subprocess
import json
from dotenv import load_dotenv
from backend import ranker  # Import the ranking model

# Load environment variables
load_dotenv()

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
TEXT_BUCKET_NAME = os.getenv("S3_EXTRACTED_TEXT_BUCKET")
PROCESSED_BUCKET_NAME = os.getenv("S3_STRUCTURED_DATA_BUCKET")

# Initialize Flask app
app = Flask(__name__, static_folder="frontend", static_url_path="")
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins

# Serve frontend files
@app.route("/")
def index():
    return send_from_directory("frontend", "index.html")

@app.route("/upload", methods=["POST"])
def upload_resume():
    """Handles resume uploads from the frontend and automates processing & ranking."""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]
        file_name = file.filename

        if not file_name:
            return jsonify({"error": "Invalid file name"}), 400

        # Upload to S3
        s3_client = boto3.client("s3", aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
        s3_client.upload_fileobj(file, BUCKET_NAME, file_name)
        print(f"✅ File uploaded to S3: {file_name}")

        # Start processing (Text Extraction + Structuring)
        process_uploaded_resume(file_name)

        # Construct extracted text & processed file URLs
        text_file_name = f"{os.path.splitext(file_name)[0]}.txt"
        processed_file_name = f"{os.path.splitext(file_name)[0]}_processed.json"
        score_file_name = f"{os.path.splitext(file_name)[0]}_score.json"

        return jsonify({
            "message": "File uploaded & processed successfully",
            "resume_file": f"https://{BUCKET_NAME}.s3.amazonaws.com/{file_name}",
            "extracted_text_file": f"https://{TEXT_BUCKET_NAME}.s3.amazonaws.com/{text_file_name}",
            "processed_data_file": f"https://{PROCESSED_BUCKET_NAME}.s3.amazonaws.com/{processed_file_name}",
            "score_file": f"https://{PROCESSED_BUCKET_NAME}.s3.amazonaws.com/{score_file_name}"
        }), 200

    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"error": str(e)}), 500

def process_uploaded_resume(file_name):
    """Triggers Textract to extract text, structures it, and ranks the resume."""
    script_textract = os.path.join("backend", "s3_textract.py")
    script_processing = os.path.join("backend", "process_text.py")

    print(f"🚀 Extracting text from S3: {file_name}")
    subprocess.run(["python", script_textract, file_name], check=True)

    print(f"📌 Structuring extracted text: {file_name}")
    subprocess.run(["python", script_processing, file_name], check=True)

    # ✅ Automate Ranking After Processing
    rank_resume_automatically(file_name)

def rank_resume_automatically(file_name):
    """Fetches extracted text, runs ranking, and stores results."""
    extracted_text_file = f"tmp/{os.path.splitext(file_name)[0]}.txt"

    with open(extracted_text_file, "r", encoding="utf-8") as f:
        resume_text = f.read()

    job_description = "Looking for a Python developer with AWS, Linux, SQL, and Git experience."
    score = ranker.rank_resume(resume_text, job_description)

    # Save ranking result
    score_file = f"tmp/{os.path.splitext(file_name)[0]}_score.json"
    with open(score_file, "w", encoding="utf-8") as f:
        json.dump({"file_name": file_name, "score": score}, f, indent=4)

    print(f"🏆 Resume '{file_name}' scored {score:.2f}%")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
