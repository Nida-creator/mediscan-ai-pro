import PyPDF2
import pytesseract
import io
from PIL import Image

def extract_text(uploaded_file) -> str:
    try:
        file_bytes = uploaded_file.read()
        filename = uploaded_file.filename.lower()
        if filename.endswith('.pdf'):
            return _from_pdf(file_bytes)
        elif filename.endswith(('.png', '.jpg', '.jpeg')):
            return _from_image(file_bytes)
        else:
            return file_bytes.decode('utf-8', errors='ignore')
    except Exception as e:
        return f"Error reading file: {str(e)}"

def _from_pdf(file_bytes) -> str:
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        return " ".join([p.extract_text() or '' for p in reader.pages]).strip()
    except Exception as e:
        return f"PDF error: {str(e)}"

def _from_image(file_bytes) -> str:
    try:
        image = Image.open(io.BytesIO(file_bytes))
        return pytesseract.image_to_string(image).strip()
    except Exception as e:
        return f"Image error: {str(e)}"
