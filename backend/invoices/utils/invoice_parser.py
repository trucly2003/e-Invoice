import tempfile
import re
from datetime import datetime
import pdfplumber
from invoices.models import Company, ExtractedInvoice, InvoiceItem, InvoiceUpload
from pdf2image import convert_from_path
import easyocr
import cloudinary
ocr_reader = easyocr.Reader(['en', 'vi'])

def normalize_text_for_matching(text: str) -> str:
    import unicodedata
    text = unicodedata.normalize("NFD", text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    text = text.lower()
    text = re.sub(r"[^a-z0-9:/\-\s\.]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def extract_text_from_pdf(file_path):
    import os
    text = ""
    with tempfile.TemporaryDirectory() as path:
        images = convert_from_path(file_path, output_folder=path)
        for idx, img in enumerate(images):
            # 🔧 Save ảnh tạm ra file PNG
            temp_image_path = os.path.join(path, f"page_{idx}.png")
            img.save(temp_image_path, "PNG")

            # 🟢 EasyOCR hoạt động tốt với đường dẫn file ảnh
            result = ocr_reader.readtext(temp_image_path, detail=0)
            text += "\n".join(result) + "\n"
    return text


def extract_text_from_pdf(file_path):
    import os
    import tempfile
    text = ""

    with tempfile.TemporaryDirectory() as path:
        # Chuyển PDF thành ảnh PNG
        images = convert_from_path(file_path, output_folder=path, fmt="png")
        for idx, img in enumerate(images):
            # 🟢 Lưu ảnh ra file .png để tránh lỗi PPM
            image_path = os.path.join(path, f"page_{idx}.png")
            img.save(image_path, "PNG")

            # ✅ Dùng đường dẫn ảnh để tránh lỗi .ppm
            result = ocr_reader.readtext(image_path, detail=0)
            text += "\n".join(result) + "\n"

    return text



def extract_invoice_info_from_text(text):
    print("========== ORIGINAL OCR TEXT ==========")
    print(text)
    normalized_text = normalize_text_for_matching(text)
    print("========== NORMALIZED OCR TEXT ==========")
    print(normalized_text)

    parsed = {
        "invoice_number": "",
        "invoice_date": None,
        "seller_name": "",
        "seller_tax": "",
        "seller_address": "",
        "buyer_name": "",
        "buyer_tax": "",
        "buyer_address": "",
        "total_amount": 0.0,
        "vat_amount": 0.0,
        "grand_total": 0.0,
        "items": []
    }

    match_invoice = re.search(r"(so|invoice no)[^\d]{0,10}(\d{6,})", normalized_text)
    if match_invoice:
        parsed["invoice_number"] = match_invoice.group(2).strip()
        print("✔️ Found invoice_number:", parsed["invoice_number"])
    else:
        print("❌ invoice_number not found")

    match_date = re.search(r"ngay (\d{1,2}) thang (\d{1,2}) nam (\d{4})", normalized_text)
    if match_date:
        try:
            day, month, year = match_date.groups()
            parsed["invoice_date"] = datetime(int(year), int(month), int(day)).date()
            print("✔️ Found invoice_date:", parsed["invoice_date"])
        except:
            print("❌ invoice_date format error")
    else:
        match_fallback_date = re.search(r"sailing date[:\-\s]*?(\d{2})[\/\-](\d{2})[\/\-](\d{4})", normalized_text)
        if match_fallback_date:
            try:
                day, month, year = match_fallback_date.groups()
                parsed["invoice_date"] = datetime(int(year), int(month), int(day)).date()
                print("✔️ Fallback invoice_date:", parsed["invoice_date"])
            except:
                print("❌ fallback invoice_date format error")
        else:
            print("❌ invoice_date not found")

    match_total = re.search(r"total amount\s*[:\-]?\s*([\d\.]+)", normalized_text)
    if match_total:
        parsed["total_amount"] = float(match_total.group(1).replace(".", ""))
        print("✔️ Found total_amount:", parsed["total_amount"])
    else:
        print("❌ total_amount not found")

    match_vat = re.search(r"vat amount\s*[:\-]?\s*([\d\.]+)", normalized_text)
    if match_vat:
        parsed["vat_amount"] = float(match_vat.group(1).replace(".", ""))
        print("✔️ Found vat_amount:", parsed["vat_amount"])
    else:
        print("❌ vat_amount not found")

    match_grand = re.search(r"grand total\s*[:\-]?\s*([\d\.]+)", normalized_text)
    if match_grand:
        parsed["grand_total"] = float(match_grand.group(1).replace(".", ""))
        print("✔️ Found grand_total:", parsed["grand_total"])
    else:
        print("❌ grand_total not found")

    match_seller = re.search(r"cong ty tnhh hapag-lloyd.*?mst[:\-]?\s*(\d[\d\s]*)", normalized_text)
    if match_seller:
        parsed["seller_name"] = "CÔNG TY TNHH HAPAG-LLOYD (VIỆT NAM)"
        parsed["seller_tax"] = match_seller.group(1).replace(" ", "").strip()
        parsed["seller_address"] = "72, Đường Lê Thánh Tôn, Phường Bến Nghé, Quận 1, TP.HCM"

    # 🟢 Tìm buyer_name sau từ 'customer :'
    match_buyer = re.search(
        r"(customer|nguo[iy] mua|ben mua)\s*[:\-]?\s*(cong ty.*?)\s+(dia chi|address|ma so thue|tax id)",
        normalized_text)

    match_serial = re.search(r"ky hieu serial\s*([a-z0-9\-]+)", normalized_text)
    if match_serial:
        parsed["serial"] = match_serial.group(1).upper()
        print("✔️ Found serial:", parsed["serial"])
    else:
        print("❌ serial not found")

    match_buyer_name = re.search(
        r"(?:customer|nguo[iy] mua|ben mua)\s*[:\-]?\s*(cong ty[^\n]*?)\s+(?:ia chi|dia chi|address|ma so thue|tax id)",
        normalized_text
    )
    if match_buyer_name:
        parsed["buyer_name"] = match_buyer_name.group(1).strip()
        print("✔️ Perfect buyer_name:", parsed["buyer_name"])
    else:
        print("❌ buyer_name not found")

    # 🟢 Tìm buyer_tax sau từ 'tax id :'
    match_buyer_tax = re.search(r"(tax id|ma so thue)\s*[:\-]?\s*([\d\s]{10,})", normalized_text)
    if match_buyer_tax:
        parsed["buyer_tax"] = match_buyer_tax.group(2).replace(" ", "").strip()
        print("✔️ Found buyer_tax:", parsed["buyer_tax"])
    else:
        print("❌ buyer_tax not found")

    # Tìm tất cả dòng có chứa 'address' hoặc 'dia chi'
    match_buyer_address = re.search(
        r"(dia chi|ia chi|address)\s*[:\-]?\s*(.+?)(ma so thue|tax id|customer code)", normalized_text
    )
    if match_buyer_address:
        parsed["buyer_address"] = match_buyer_address.group(2).strip()
        print("✔️ Found buyer_address:", parsed["buyer_address"])
    else:
        print("❌ buyer_address not found")

    return parsed

def extract_invoice_from_file(upload_obj):
    file_path = upload_obj.file.path

    if upload_obj.file_type == "PDF":
        text = extract_text_from_pdf(file_path)
    else:
        text = extract_text_from_image(file_path)

    parsed = extract_invoice_info_from_text(text)

    seller, _ = Company.objects.get_or_create(
        tax_code=parsed["seller_tax"],
        defaults={"name": parsed["seller_name"], "address": parsed["seller_address"]}
    )

    # Tạo hoặc cập nhật buyer
    buyer, created = Company.objects.get_or_create(
        tax_code=parsed["buyer_tax"],
        defaults={"name": parsed["buyer_name"], "address": parsed["buyer_address"]}
    )

    if not created:
        updated = False
        if buyer.name != parsed["buyer_name"]:
            buyer.name = parsed["buyer_name"]
            updated = True
        if buyer.address != parsed["buyer_address"]:
            buyer.address = parsed["buyer_address"]
            updated = True
        if updated:
            buyer.save()

    invoice = ExtractedInvoice.objects.create(
        upload=upload_obj,
        invoice_number=parsed["invoice_number"],
        invoice_date=parsed["invoice_date"],
        seller=seller,
        buyer=buyer,
        total_amount=parsed["total_amount"],
        vat_amount=parsed["vat_amount"],
        grand_total=parsed["grand_total"],
        serial = parsed.get("serial", "")
    )

    if upload_obj.file_type == "PDF":
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                table = page.extract_table()
                if table:
                    for row in table:
                        if row and len(row) >= 6 and row[0] and row[0] != "Tên hàng hóa, dịch vụ":
                            try:
                                item_name = row[0].strip().replace("\n", " ")
                                unit = row[1].strip()
                                quantity = int(re.sub(r"[^0-9]", "", row[2])) if re.sub(r"[^0-9]", "", row[2]) else 0
                                unit_price = float(row[3].replace(".", "").replace(",", ".")) if row[3] else 0.0
                                amount = float(row[4].replace(".", "").replace(",", ".")) if row[4] else 0.0
                                tax_rate = float(re.sub(r"[^0-9\\.]", "", row[5])) if row[5] else 0.0
                                tax_amount = float(row[6].replace(".", "").replace(",", ".")) if len(row) > 6 and row[6] else 0.0

                                InvoiceItem.objects.create(
                                    invoice=invoice,
                                    item_name=item_name,
                                    unit=unit,
                                    quantity=quantity,
                                    unit_price=unit_price,
                                    amount=amount,
                                    tax_rate=tax_rate,
                                    tax_amount=tax_amount
                                )
                            except Exception as e:
                                print(f"⚠️ Lỗi khi xử lý hàng hóa: {e}")

    file_path = upload_obj.file.path
    result = cloudinary.uploader.upload(file_path, folder="invoices")
    cloudinary_url = result.get("secure_url")

    # Xóa file local sau khi upload xong
    upload_obj.file.delete(save=False)

    upload_obj.cloudinary_url = cloudinary_url
    upload_obj.save()

    print("✔️ Uploaded to Cloudinary:", cloudinary_url)

    return invoice
