import os
import tempfile
import re
import easyocr
from pdf2image import convert_from_path
import unicodedata
import pdfplumber

reader = easyocr.Reader(['en', 'vi'], gpu=False)


def normalize_text_for_db(text: str) -> str:
    text = unicodedata.normalize("NFD", text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    text = text.lower()
    text = re.sub(r"[^a-z0-9:/\-\.\s]", " ", text)  # Giữ lại dấu cần thiết
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def extract_text_from_pdf(pdf_path):
    raw_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                raw_text += page_text + "\n"

    normalized = normalize_text_for_db(raw_text)

    print("🧾 PDF TEXT (raw):\n", raw_text)
    print("🧾 PDF TEXT (normalized):\n", normalized)

    return raw_text, normalized


# ✅ OCR cho ảnh
def extract_text_from_image(image_path):
    result = reader.readtext(image_path, detail=0)
    raw_text = "\n".join(result)
    normalized = normalize_text_for_db(raw_text)

    print("🖼️ OCR TEXT (raw):\n", raw_text)
    print("🖼️ OCR TEXT (normalized):\n", normalized)

    return raw_text, normalized
