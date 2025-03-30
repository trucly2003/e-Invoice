# import xml.etree.ElementTree as ET
# import pdfplumber
# import os
# import re
# import datetime
# from django.db import transaction
# from invoices.models import EmailInvoice, Invoice, Buyer, Seller, InvoiceItem
#
# DOWNLOAD_FOLDER = r"D:\TaiLieuHocTap\khoaluantotnghiep\e-Invoice\e_invoice_app\invoices\downloads"
#
# def get_latest_file(file_type):
#     """Lấy file mới nhất từ thư mục tải về theo loại file (xml hoặc pdf)."""
#     files = [f for f in os.listdir(DOWNLOAD_FOLDER) if f.endswith(f".{file_type}")]
#     if not files:
#         return None
#     latest_file = max(files, key=lambda f: os.path.getctime(os.path.join(DOWNLOAD_FOLDER, f)))
#     return os.path.join(DOWNLOAD_FOLDER, latest_file)
#
# def convert_issue_date(issue_date_str):
#     """Chuyển đổi ngày hóa đơn từ dạng `07 tháng 10 năm 2024` về `YYYY-MM-DD`"""
#     try:
#         months = {
#             "tháng 1": "01", "tháng 2": "02", "tháng 3": "03", "tháng 4": "04",
#             "tháng 5": "05", "tháng 6": "06", "tháng 7": "07", "tháng 8": "08",
#             "tháng 9": "09", "tháng 10": "10", "tháng 11": "11", "tháng 12": "12"
#         }
#         parts = issue_date_str.split()
#         day = parts[0].zfill(2)
#         month = months.get(f"{parts[1]} {parts[2]}", "01")
#         year = parts[-1]
#         return f"{year}-{month}-{day}"
#     except Exception as e:
#         print(f"❌ Lỗi khi chuyển đổi ngày hóa đơn: {e}")
#         return None
#
#
# def extract_from_xml():
#     """Trích xuất dữ liệu từ file XML"""
#     xml_file = get_latest_file("xml")
#     if not xml_file:
#         print("⚠ Không tìm thấy file XML để xử lý.")
#         return None, None, None, {}, {}, []
#
#     print(f"📥 Đang xử lý file XML: {xml_file}")
#     tree = ET.parse(xml_file)
#     root = tree.getroot()
#
#     dlh_don = root.find(".//DLHDon")
#     if dlh_don is None:
#         print("❌ Không tìm thấy `<DLHDon>` trong XML!")
#         return "UNKNOWN", "0000-00-00", "0", {}, {}, []
#
#     tt_chung = dlh_don.find("TTChung")
#     if tt_chung is None:
#         print("❌ Không tìm thấy `<TTChung>` trong XML!")
#         return "UNKNOWN", "0000-00-00", "0", {}, {}, []
#
#     # 🏷 Trích xuất dữ liệu hóa đơn
#     invoice_number = tt_chung.findtext("SHDon", "UNKNOWN").strip()
#     issue_date = tt_chung.findtext("NLap", "0000-00-00").strip()
#
#     # 🏢 Thông tin người bán
#     nb = dlh_don.find(".//NBan")
#     seller_data = {
#         "name": nb.findtext("Ten", "Unknown Seller").strip(),
#         "tax_code": nb.findtext("MST", "Unknown").strip(),
#         "address": nb.findtext("DChi", "Unknown Address").strip()
#     }
#
#     # 🛒 Thông tin người mua
#     nm = dlh_don.find(".//NMua")
#     buyer_data = {
#         "name": nm.findtext("Ten", "Unknown Buyer").strip(),
#         "tax_code": nm.findtext("MST", "Unknown").strip(),
#         "address": nm.findtext("DChi", "Unknown Address").strip()
#     }
#
#     # 💰 Lấy tổng tiền hóa đơn
#     ttoan = dlh_don.find(".//NDHDon/TToan")  # Đúng XPath để tìm tổng tiền
#     if ttoan is not None:
#         raw_total_amount = ttoan.findtext("TgTTTBSo", "0").strip()
#         print(f"🧐 Giá trị raw total_amount trước khi xử lý: {raw_total_amount}")  # Debug
#
#         # Xử lý trường hợp tổng tiền có dấu chấm phân cách (ví dụ: "15.157.896")
#         total_amount = raw_total_amount.replace(".", "").replace(",", ".")
#
#         try:
#             total_amount = float(total_amount)
#         except ValueError:
#             print(f"⚠ Lỗi chuyển đổi `total_amount`: {raw_total_amount}")
#             total_amount = 0.0
#     else:
#         print("❌ Không tìm thấy `<TToan>` trong XML!")
#         total_amount = 0.0
#
#     # 📦 Lấy danh sách hàng hóa
#     items = []
#     dshhdvu = dlh_don.find(".//NDHDon/DSHHDVu")  # Đúng XPath của hàng hóa
#     if dshhdvu is None:
#         print("❌ Không tìm thấy `<DSHHDVu>` trong XML!")
#     else:
#         for item in dshhdvu.findall("HHDVu"):
#             item_name = item.findtext("THHDVu", "Unknown Item").strip()
#             unit = item.findtext("DVTinh", "N/A").strip()
#
#             try:
#                 quantity = int(item.findtext("SLuong", "0").strip())
#             except ValueError:
#                 quantity = 0
#
#             try:
#                 unit_price = float(item.findtext("DGia", "0").strip())
#             except ValueError:
#                 unit_price = 0.0
#
#             try:
#                 amount = float(item.findtext("ThTien", "0").strip())
#             except ValueError:
#                 amount = 0.0
#
#             items.append({
#                 "item_name": item_name,
#                 "unit": unit,
#                 "quantity": quantity,
#                 "unit_price": unit_price,
#                 "amount": amount
#             })
#
#     return invoice_number, issue_date, total_amount, seller_data, buyer_data, items
#
#
# def extract_from_pdf():
#     """Trích xuất dữ liệu từ file PDF"""
#     pdf_file = get_latest_file("pdf")
#     if not pdf_file:
#         return None, None, None, None, None, []
#
#     print(f"📥 Đang xử lý file PDF: {pdf_file}")
#     data = {
#         "invoice_number": "",
#         "issue_date": "",
#         "seller": {},
#         "buyer": {},
#         "items": [],
#         "total_amount": 0.0,
#         "vat_amount": 0.0,
#         "grand_total": 0.0,
#         "serial": "",
#     }
#
#     with pdfplumber.open(pdf_file) as pdf:
#         text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
#         lines = text.split("\n")  # Chia thành từng dòng để dễ xử lý
#
#         # ✅ Trích xuất Serial
#         match_serial = re.search(r"Ký hiệu \(Serial No.\) ?: (\w+)", text)
#         serial = match_serial.group(1) if match_serial else "UNKNOWN"
#
#         # ✅ Trích xuất số hóa đơn
#         match_invoice = re.search(r"Số \(Invoice No.\) ?: (\d+)", text)
#         invoice_number = match_invoice.group(1) if match_invoice else "UNKNOWN"
#
#         # ✅ Trích xuất ngày lập
#         match_date = re.search(r"Ngày (\d{2}) tháng (\d{2}) năm (\d{4})", text)
#         issue_date = f"{match_date.group(3)}-{match_date.group(2)}-{match_date.group(1)}" if match_date else "0000-00-00"
#
#         data["serial"] = serial
#         data["invoice_number"] = invoice_number
#         data["issue_date"] = issue_date
#
#         # ✅ Trích xuất thông tin người bán (Seller)
#         seller_name, seller_tax, seller_address = "", "", ""
#         for i, line in enumerate(lines):
#             if "CÔNG TY TNHH" in line:  # Dòng chứa tên công ty
#                 seller_name = line.strip()
#             if "MST:" in line:  # Dòng chứa mã số thuế
#                 seller_tax = re.sub(r"[^\d]", "", line)  # Lọc chỉ lấy số MST
#             if line.strip().startswith("Số"):  # Dòng chứa địa chỉ (bắt đầu bằng "Số")
#                 seller_address = line.strip()
#                 break  # Dừng khi đã lấy đủ thông tin
#
#         if seller_tax:
#             data["seller"] = {
#                 "name": seller_name,
#                 "tax_code": seller_tax,
#                 "address": seller_address
#             }
#             print(f"🏢 Người bán: {data['seller']}")  # Debugging Log
#         else:
#             print("❌ Không tìm thấy thông tin người bán!")
#
#         # ✅ Trích xuất thông tin người mua (Buyer)
#         match_buyer = re.search(
#             r"Đơn vị mua \(Customer\):\s+(.*?)\nĐịa chỉ \(Address\):\s+(.*?)\nMã số thuế \(Tax ID\):\s+([\d\s]+)", text,
#             re.DOTALL)
#         if match_buyer:
#             data["buyer"] = {
#                 "name": match_buyer.group(1).strip(),
#                 "address": match_buyer.group(2).strip().replace("\n", " "),
#                 "tax_code": match_buyer.group(3).replace(" ", "").strip()
#             }
#             print(f"🛒 Người mua: {data['buyer']}")  # Debugging Log
#         else:
#             print("❌ Không tìm thấy thông tin người mua!")
#
#         # ✅ Trích xuất danh sách hàng hóa từ bảng PDF
#         for page in pdf.pages:
#             table = page.extract_table()
#             if not table:
#                 print(f"⚠ Không có bảng trên trang {page.page_number}")
#                 continue
#
#             for row in table:
#                 if any(keyword in row[0] for keyword in ["Đơn vị", "Freight charges", "Số lượng"]):
#                     continue  # Bỏ qua dòng tiêu đề
#
#                 print(f"🔍 Dữ liệu hàng hóa: {row}")  # Debugging log
#
#                 if row and len(row) >= 6:  # Đảm bảo có đủ cột
#                     try:
#                         item_name = row[0].strip().replace("\n", " ")
#                         unit = row[1].strip()
#                         quantity = int(row[2].replace(",", "").strip())
#                         unit_price = float(row[3].replace(".", "").replace(",", ".").strip())
#                         amount = float(row[4].replace(".", "").replace(",", ".").strip())
#
#                         # Xử lý lỗi tax_rate có chứa "KHAC :\n"
#                         raw_tax_rate = row[5].replace("KHAC :", "").replace("\n", "").replace("%", "").strip()
#                         raw_tax_rate = raw_tax_rate.replace(",", ".")
#
#                         tax_rate = float(raw_tax_rate) if raw_tax_rate else 0.0
#                         tax_amount = float(row[6].replace(".", "").replace(",", ".").strip()) if len(row) > 6 else 0.0
#
#                         data["items"].append({
#                             "item_name": item_name,
#                             "unit": unit,
#                             "quantity": quantity,
#                             "unit_price": unit_price,
#                             "amount": amount,
#                             "tax_rate": tax_rate,
#                             "tax_amount": tax_amount,
#                         })
#                     except ValueError as e:
#                         print(f"⚠ Lỗi khi xử lý hàng hóa: {row} | Lỗi: {e}")
#
#         # ✅ Trích xuất tổng tiền
#         match_total = re.search(r"Cộng tiền hàng, dịch vụ \(Total amount\):\s+([\d\.]+)", text)
#         match_vat = re.search(r"Tổng cộng tiền thuế \(VAT amount\):\s+([\d\.]+)", text)
#         match_grand_total = re.search(r"Tổng cộng tiền thanh toán \(Grand total\):\s+([\d\.]+)", text)
#
#         data["total_amount"] = float(match_total.group(1).replace(".", "")) if match_total else 0.0
#         data["vat_amount"] = float(match_vat.group(1).replace(".", "")) if match_vat else 0.0
#         data["grand_total"] = float(match_grand_total.group(1).replace(".", "")) if match_grand_total else 0.0
#     return data
#
#
# def save_data(invoice_number, issue_date, total_amount, seller_data, serial,buyer_data, items, source_type="XML", vat_amount=0.0, grand_total=0.0):
#     """Lưu dữ liệu hóa đơn vào database (hỗ trợ XML & PDF)."""
#     with transaction.atomic():
#         if not invoice_number or invoice_number == "UNKNOWN":
#             print("❌ Lỗi: invoice_number không hợp lệ!")
#             return None
#
#         # ✅ Chuyển đổi `issue_date` về đúng định dạng YYYY-MM-DD
#         try:
#             issue_date = datetime.datetime.strptime(issue_date, "%Y-%m-%d").date()
#         except ValueError:
#             print("❌ Lỗi: issue_date không đúng định dạng YYYY-MM-DD!")
#             return None
#
#         # ✅ Đảm bảo `total_amount`, `vat_amount`, `grand_total` là số hợp lệ
#         try:
#             total_amount = float(total_amount) if total_amount else 0.0
#             vat_amount = float(vat_amount) if vat_amount else 0.0
#             grand_total = float(grand_total) if grand_total else total_amount
#         except ValueError:
#             print("❌ Lỗi: Giá trị số không hợp lệ!")
#             return None
#
#         # ✅ Kiểm tra hoặc tạo `EmailInvoice`
#         email_invoice, _ = EmailInvoice.objects.update_or_create(
#             invoice_number=invoice_number,
#             defaults={"company_name": seller_data.get("name", "Unknown")}
#         )
#
#         # ✅ Kiểm tra hoặc tạo `Seller`
#         seller, _ = Seller.objects.get_or_create(
#             tax_code=seller_data.get("tax_code", "Unknown"),
#             defaults={
#                 "name": seller_data.get("name", "Unknown Seller"),
#                 "address": seller_data.get("address", "Unknown Address")
#             }
#         )
#
#         # ✅ Kiểm tra hoặc tạo `Buyer`
#         buyer, _ = Buyer.objects.get_or_create(
#             tax_code=buyer_data.get("tax_code", "Unknown"),
#             defaults={
#                 "name": buyer_data.get("name", "Unknown Buyer"),
#                 "address": buyer_data.get("address", "Unknown Address")
#             }
#         )
#
#         # ✅ Kiểm tra hóa đơn có tồn tại không với `invoice_number` và `source_type`
#         existing_invoice = Invoice.objects.filter(invoice_number=invoice_number, source_type=source_type).first()
#
#         if existing_invoice:
#             # ✅ Nếu `invoice_number + source_type` đã tồn tại, chỉ cập nhật dữ liệu
#             existing_invoice.issue_date = issue_date
#             existing_invoice.total_amount = total_amount
#             existing_invoice.vat_amount = vat_amount
#             existing_invoice.grand_total = grand_total
#             existing_invoice.buyer = buyer
#             existing_invoice.seller = seller
#             existing_invoice.email_invoice = email_invoice
#             existing_invoice.save()
#             print(f"🔄 Hóa đơn {invoice_number} ({source_type}) đã được cập nhật.")
#         else:
#             # ✅ Nếu `source_type` khác, tạo bản ghi mới mà không ghi đè lên bản cũ
#             existing_invoice = Invoice.objects.create(
#                 serial=serial,
#                 issue_date=issue_date,
#                 total_amount=total_amount,
#                 vat_amount=vat_amount,
#                 grand_total=grand_total,
#                 source_type=source_type,
#                 buyer=buyer,
#                 seller=seller,
#                 email_invoice=email_invoice,
#             )
#             print(f"✅ Hóa đơn {invoice_number} ({source_type}) đã được tạo mới.")
#
#         # ✅ Xóa danh sách sản phẩm cũ trước khi lưu mới nếu dữ liệu thay đổi
#         InvoiceItem.objects.filter(invoice=existing_invoice).delete()
#
#         # ✅ Lưu danh sách sản phẩm
#         for item in items:
#             try:
#                 InvoiceItem.objects.create(
#                     invoice=existing_invoice,
#                     item_name=item.get("item_name", "Unknown Item"),
#                     unit=item.get("unit", "N/A"),
#                     quantity=int(item.get("quantity", 0)),
#                     unit_price=float(item.get("unit_price", 0.0)),
#                     amount=float(item.get("amount", 0.0)),
#                     tax_rate=float(item.get("tax_rate", 0.0)),
#                     tax_amount=float(item.get("tax_amount", 0.0))
#                 )
#             except ValueError as e:
#                 print(f"⚠ Lỗi khi lưu sản phẩm: {item} | Lỗi: {e}")
#
#     print(f"✅ Hóa đơn {invoice_number} ({source_type}) đã lưu vào database!")
#     return existing_invoice