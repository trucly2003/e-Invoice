import os
import tempfile
import re
import easyocr
from pdf2image import convert_from_path
import unicodedata

ocr_reader = easyocr.Reader(['en', 'vi'])

def normalize_text_for_matching(text: str) -> str:
    text = unicodedata.normalize("NFD", text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    text = text.lower()
    text = re.sub(r"[^a-z0-9:/\\-\\s\\.]", " ", text)
    text = re.sub(r"\\s+", " ", text)
    return text.strip()

import os
import tempfile
from pdf2image import convert_from_path
import easyocr

reader = easyocr.Reader(['en', 'vi'])

def extract_text_from_pdf(pdf_path):
    text = ""
    with tempfile.TemporaryDirectory() as path:
        images = convert_from_path(pdf_path, output_folder=path, fmt="png")
        for idx, img in enumerate(images):
            image_path = os.path.join(path, f"page_{idx}.png")
            img.save(image_path, "PNG")
            result = reader.readtext(image_path, detail=0)
            text += "\n".join(result) + "\n"
            print("🧾 OCR TEXT:\n", text)

    return text

def extract_text_from_image(image_path):
    result = ocr_reader.readtext(image_path, detail=0)
    return "\n".join(result)
