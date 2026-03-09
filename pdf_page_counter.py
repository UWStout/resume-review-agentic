import sys
from os import path
from pathlib import Path
from pypdf import PdfReader

INPUT_FOLDER = path.join("pdf_data", "karmaker-submissions")

file_list = [entry for entry in Path(INPUT_FOLDER).iterdir() if entry.is_file() and Path(entry.name).suffix == ".pdf"]
if len(file_list) < 1:
    print("No PDF files found in {INPUT_DIR}")
    sys.exit(1)

for resume_name in [item.name for item in file_list]:
    with open(path.join(INPUT_FOLDER, resume_name), "rb") as pdf_file:
        reader = PdfReader(pdf_file)
        print(f"{resume_name}: {len(reader.pages)}")
