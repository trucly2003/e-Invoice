import os
from dotenv import load_dotenv

# Load biến môi trường từ file .env
load_dotenv()

DB_CONFIG = {
    "dbname": "invoice_checker",
    "user": "invoice_user",
    "password": os.getenv("nguyenthitrucly2003"),
    "host": "localhost",
    "port": "5432"
}

# Đường dẫn Tesseract OCR (nếu có)
TESSERACT_PATH = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
