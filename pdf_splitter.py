import json
from pypdf import PdfReader, PdfWriter

# Path to a JSON file with information about how to split up the resumes
PAGE_DATA_FILE = "./pageData.json"

# Path to the combined PDF that you want to split
COMBINED_PDF_FILE = "./pdf_data/Resume Books_110.pdf"

# Folder to write the extracted files to
OUTPUT_PATH = "./pdf_data"

# Read in the PDF splitting data
with open(PAGE_DATA_FILE, "r") as file:
    data = json.load(file)

# Open the combined PDF file in binary read mode
with open(COMBINED_PDF_FILE, "rb") as pdf_file:
    # Create a PDF reader object
    reader = PdfReader(pdf_file)

    # Loop over the values in the data to split up the combined file
    page_offset = 0
    for output_index in range(0, len(data)):
        # Build an output filename
        output_filename = f"{data[output_index]["filename"]}.pdf"

        # Should we skip this one or not (negative or zero page values are skipped)
        if data[output_index]["pages"] <= 0:
            page_offset += -data[output_index]["pages"]
        else:
            # Create a PDF writer object for the new file
            writer = PdfWriter()

            # Add the desired pages to the writer object
            raw_count = data[output_index]["pages"]
            while raw_count > 0:
                page = reader.pages[page_offset]
                writer.add_page(page)
                page_offset += 1
                raw_count -= 1

            # Save the new pages as a new file in binary write mode
            with open(f"{OUTPUT_PATH}/{output_filename}", "wb") as output_file:
                writer.write(output_file)
