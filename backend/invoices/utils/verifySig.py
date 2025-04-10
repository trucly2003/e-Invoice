import subprocess
import fitz  # PyMuPDF
import requests
import tempfile
import os

def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def check_pdf_signature_windows(pdf_path):
    try:
        cygwin_pdf_path = pdf_path.replace("C:\\", "/cygdrive/c/").replace("\\", "/")
        command = ['C:\\cygwin64\\bin\\bash.exe', '-c', f'pdfsig "{cygwin_pdf_path}"']
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stdout

        if "Signature validation: ok" in output.lower():
            status = "PASS"
        elif "Signature validation: failed" in output.lower():
            status = "FAIL"
        else:
            status = "UNKNOWN"

        signer_name = ""
        for line in output.splitlines():
            if "Signer Certificate Common Name" in line:
                signer_name = line.split(":", 1)[1].strip()

        return {
            "status": status,
            "signer_name": signer_name,
            "raw_output": output
        }

    except Exception as e:
        return {
            "status": "FAIL",
            "signer_name": "",
            "raw_output": str(e)
        }


def download_cloud_file_temp(url):
    response = requests.get(url)
    content_type = response.headers.get("Content-Type", "")

    if "pdf" not in content_type.lower():
        raise Exception(f"Invalid content type: {content_type}")

    tmp_dir = "C:/pdf_temp_files"
    os.makedirs(tmp_dir, exist_ok=True)
    tmp_path = os.path.join(tmp_dir, "downloaded_invoice.pdf")

    with open(tmp_path, "wb") as f:
        f.write(response.content)

    # 🔍 Kiểm tra size file
    size = os.path.getsize(tmp_path)
    print(f"📏 Tệp PDF sau khi tải: {size} bytes")

    if size == 0:
        raise Exception(f"Downloaded file is empty: {tmp_path}")

    return tmp_path
