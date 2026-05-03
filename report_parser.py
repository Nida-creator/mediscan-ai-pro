import PyPDF2
import pytesseract
from PIL import Image
import io

def extract_text(uploaded_file) -> str:
    '''Extract text from PDF or image uploaded via Flask'''
    try:
        # Read file bytes
        file_bytes = uploaded_file.read()
        filename = uploaded_file.filename.lower()

        if filename.endswith('.pdf'):
            return _extract_from_pdf_bytes(file_bytes)
        elif filename.endswith(('.png', '.jpg', '.jpeg')):
            return _extract_from_image_bytes(file_bytes)
        else:
            return file_bytes.decode('utf-8', errors='ignore')

    except Exception as e:
        return f"Error reading file: {str(e)}"


def _extract_from_pdf_bytes(file_bytes) -> str:
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        text = ''
        for page in reader.pages:
            text += page.extract_text() or ''
        return text.strip()
    except Exception as e:
        return f"PDF error: {str(e)}"


def _extract_from_image_bytes(file_bytes) -> str:
    try:
        image = Image.open(io.BytesIO(file_bytes))
        return pytesseract.image_to_string(image).strip()
    except Exception as e:
        return f"Image error: {str(e)}"
