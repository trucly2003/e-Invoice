# import subprocess
# import fitz  # PyMuPDF
#
# def extract_text_from_pdf(pdf_path):
#     """
#     Trích toàn bộ text từ file PDF (để so khớp với tên người ký)
#     """
#     text = ""
#     with fitz.open(pdf_path) as doc:
#         for page in doc:
#             text += page.get_text()
#     return text
#
#
# def check_pdf_signature(pdf_path):
#     """
#     Dùng lệnh `pdfsig` để trích xuất thông tin chữ ký điện tử từ file PDF
#     """
#     try:
#         result = subprocess.run(
#             ['pdfsig', pdf_path],
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             text=True
#         )
#         output = result.stdout
#
#         # Xác định trạng thái chữ ký
#         if "Signature validation: ok" in output.lower():
#             status = "PASS"
#         elif "Signature validation: failed" in output.lower():
#             status = "FAIL"
#         else:
#             status = "UNKNOWN"
#
#         signer_name = ""
#         for line in output.splitlines():
#             if "Signer Certificate Common Name" in line:
#                 signer_name = line.split(":", 1)[1].strip()
#
#         return {
#             "status": status,
#             "signer_name": signer_name,
#             "raw_output": output
#         }
#
#     except Exception as e:
#         return {
#             "status": "FAIL",
#             "signer_name": "",
#             "raw_output": str(e)
#         }
