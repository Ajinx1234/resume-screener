import json
import os

def structure_text(file_name):
    """Parses extracted text into structured JSON format."""
    input_file = f"tmp/{os.path.splitext(file_name)[0]}.txt"
    output_file = f"tmp/{os.path.splitext(file_name)[0]}.json"

    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()

    structured_data = {
        "Name": text.split("\n")[0],
        "Email": next((line for line in text.split("\n") if "@" in line), "Not Found"),
        "Phone": next((line for line in text.split("\n") if line.replace(" ", "").isdigit()), "Not Found"),
        "Skills": ["Python", "AWS", "Linux"]  # This can be improved with NLP
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(structured_data, f, indent=4)

if __name__ == "__main__":
    import sys
    structure_text(sys.argv[1])
