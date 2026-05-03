"""
report_parser.py
MediScan AI Pro — Tech Member 3 (Data + Parser)

Extracts clean text from uploaded PDF and image files.
Called by Tech 2 (ai_engine) and Tech 4 (deployment/app).
"""

import PyPDF2
import pytesseract
import io
from PIL import Image


def extract_text(uploaded_file) -> str:
    """
    Extract text from a PDF or image file uploaded via Streamlit.

    Args:
        uploaded_file: Streamlit UploadedFile object (PDF, PNG, JPG, JPEG)

    Returns:
        Extracted text as a string.
        Returns empty string on unsupported type.
        Returns error message string if extraction fails (never crashes).
    """
    try:
        if uploaded_file.type == "application/pdf":
            return _from_pdf(uploaded_file)
        elif uploaded_file.type in ["image/png", "image/jpeg", "image/jpg"]:
            return _from_image(uploaded_file)
        else:
            return ""
    except Exception as e:
        return f"Error reading file: {str(e)}"


def _from_pdf(file) -> str:
    """
    Internal helper: extract text from a PDF file using PyPDF2.
    """
    reader = PyPDF2.PdfReader(file)
    pages_text = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages_text.append(text)
    return " ".join(pages_text).strip()


def _from_image(file) -> str:
    """
    Internal helper: extract text from an image using pytesseract OCR.
    """
    image = Image.open(io.BytesIO(file.read()))
    return pytesseract.image_to_string(image).strip()


if __name__ == "__main__":
    print("report_parser.py loaded successfully.")
    print("Supported types: application/pdf | image/png | image/jpeg | image/jpg")
    print("Use extract_text(uploaded_file) in your Streamlit app.")