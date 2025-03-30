# import unicodedata
# import re
# from rapidfuzz import fuzz
# from invoices.models import Invoice, CrawledCompanyData
# from invoices.utils.crawler import crawl_taxcode_data
#
# #check trên trang mã số thuế
# def normalize_text(text: str) -> str:
#     """Chuẩn hóa tên công ty hoặc địa chỉ"""
#     if not text:
#         return ""
#
#     text = unicodedata.normalize("NFD", text)
#     text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
#     text = text.lower()
#
#     # Bỏ các từ không quan trọng và tiền tố phổ biến
#     replacements = {
#         "cong ty tnhh": "",
#         "cty tnhh": "",
#         "cong ty co phan": "",
#         "cty co phan": "",
#         "cong ty": "",
#         "cty": "",
#         "co phan": "",
#         "trach nhiem huu han": "",
#         "quoc te": "",
#         "viet nam": "",
#         "vn": "",
#     }
#
#     for key, val in replacements.items():
#         text = text.replace(key, val)
#
#     text = re.sub(r'[^a-z0-9\s]', ' ', text)  # Bỏ ký tự đặc biệt
#     text = re.sub(r'\s+', ' ', text).strip()  # Xóa khoảng trắng thừa
#
#     return text
#
#
#
# def is_relative_match(text1: str, text2: str, threshold: int = 80) -> bool:
#     """So sánh tương đối 2 chuỗi đã chuẩn hóa"""
#     norm1 = normalize_text(text1)
#     norm2 = normalize_text(text2)
#     score = fuzz.token_sort_ratio(norm1, norm2)
#     print(f"🔍 So sánh: {norm1} ↔ {norm2} | Điểm: {score}")
#     return score >= threshold
#
# def verify_invoice_and_compare(invoice_id):
#     """Crawl dữ liệu MST và so sánh với dữ liệu trích xuất từ file."""
#     try:
#         invoice = Invoice.objects.get(id=invoice_id)
#
#         # 📌 Crawl dữ liệu cho người bán
#         seller_tax = invoice.seller.tax_code
#         crawled_seller = crawl_taxcode_data(seller_tax)
#         if crawled_seller:
#             invoice.crawled_seller = CrawledCompanyData.objects.get(tax_code=seller_tax)
#
#         # 📌 Crawl dữ liệu cho người mua
#         buyer_tax = invoice.buyer.tax_code
#         crawled_buyer = crawl_taxcode_data(buyer_tax)
#         if crawled_buyer:
#             invoice.crawled_buyer = CrawledCompanyData.objects.get(tax_code=buyer_tax)
#
#         invoice.save()
#
#         result = {
#             "invoice_number": invoice.serial,
#             "seller_tax_code": seller_tax,
#             "buyer_tax_code": buyer_tax,
#
#             "seller_match": {
#                 "name_match": is_relative_match(invoice.seller.name, invoice.crawled_seller.name),
#                 "address_match": is_relative_match(invoice.seller.address, invoice.crawled_seller.address)
#             },
#             "buyer_match": {
#                 "name_match": is_relative_match(invoice.buyer.name, invoice.crawled_buyer.name),
#                 "address_match": is_relative_match(invoice.buyer.address, invoice.crawled_buyer.address)
#             },
#
#             "seller_extracted": {
#                 "name": invoice.seller.name,
#                 "address": invoice.seller.address
#             },
#             "seller_crawled": {
#                 "name": invoice.crawled_seller.name,
#                 "address": invoice.crawled_seller.address,
#                 "status": invoice.crawled_seller.status
#             },
#
#             "buyer_extracted": {
#                 "name": invoice.buyer.name,
#                 "address": invoice.buyer.address
#             },
#             "buyer_crawled": {
#                 "name": invoice.crawled_buyer.name,
#                 "address": invoice.crawled_buyer.address,
#                 "status": invoice.crawled_buyer.status
#             }
#         }
#
#         return result
#
#     except Invoice.DoesNotExist:
#         return {"error": "Hóa đơn không tồn tại"}
#     except Exception as e:
#         return {"error": str(e)}
