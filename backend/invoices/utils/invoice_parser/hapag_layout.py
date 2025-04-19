import re
from datetime import datetime

def parse(text: str) -> dict:
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
        "link_tra_cuu": "",
        "ma_tra_cuu": "",
        "serial": "",
        "items": []
    }

    # 🧾 Invoice number
    match_invoice = re.search(r"(so|invoice no)[^\d]{0,10}(\d{6,})", text)
    if match_invoice:
        parsed["invoice_number"] = match_invoice.group(2).strip()

    # 📅 Invoice date
    match_date = re.search(r"ngay (\d{1,2}) thang (\d{1,2}) nam (\d{4})", text)
    if match_date:
        day, month, year = match_date.groups()
        parsed["invoice_date"] = datetime(int(year), int(month), int(day)).date()

    # 🏷️ Serial
    match_serial = re.search(r"(serial[\s:\-]*)([a-zA-Z0-9]{4,})", text)
    if match_serial:
        parsed["serial"] = match_serial.group(2).upper()
    else:
        match_serial = re.search(r"\b(c\d{2}[a-z]{3})\b", text)
        if match_serial:
            parsed["serial"] = match_serial.group(1).upper()

    # 🏢 Seller name
    match_seller_name = re.search(r"(cong ty tnhh[^\n\r]{0,80})", text)
    if match_seller_name:
        name_raw = match_seller_name.group(1).strip()
        name_cut = re.split(r"(hoa|mst|ma so thue|ngay|serial)", name_raw)[0].strip()
        parsed["seller_name"] = name_cut

    # 🧾 Seller tax
    match_seller_tax = re.search(r"(mst|ma so thue)\s*[:\-]?\s*([\d\s]{10,})", text)
    if match_seller_tax:
        parsed["seller_tax"] = match_seller_tax.group(2).replace(" ", "").strip()

    # 📍 Seller address – match sau "serial no", bắt đầu từ số và dừng lại trước từ khóa như "so invoice no"
    match_seller_address = re.search(
        r"(?:serial no\.?\s*:\s*[a-z0-9]+)?\s*(\d{2,4}\s+(uong|duong|phuong)[^\n\r]{10,80}?)\s+(so invoice no|ref no|thanh pho|viet nam)",
        text
    )
    if match_seller_address:
        parsed["seller_address"] = match_seller_address.group(1).strip()

    # 👤 Buyer name – loại "ia chi" nếu dính OCR sai
    match_buyer_name = re.search(
        r"(?:customer|nguoi mua|ben mua)\s*[:\-]?\s*(cong ty[^\n\r]*?)\s*(?=(address|dia chi|ma so thue|tax id|customer code|mst))",
        text
    )
    if match_buyer_name:
        name = match_buyer_name.group(1).strip()
        parsed["buyer_name"] = re.sub(r"\bia chi\b", "", name).strip()

    # 🔑 Mã tra cứu
    match_mtc = re.search(r"ma tra cuu.*?[:\-]?\s*([a-z0-9]{8,})", text)
    if match_mtc:
        parsed["ma_tra_cuu"] = match_mtc.group(1).strip().upper()

    # 🌐 Link tra cứu
    if "tracuu" in text and "ehoadon" in text:
        parsed["link_tra_cuu"] = "http://tracuu.ehoadon.vn"

    # 🧾 Buyer tax
    match_buyer_tax = re.search(r"(tax id|ma so thue)\s*[:\-]?\s*([\d\s]{10,})", text)
    if match_buyer_tax:
        parsed["buyer_tax"] = match_buyer_tax.group(2).replace(" ", "").strip()

    # 🏠 Buyer address
    match_buyer_address = re.search(
        r"(?:address|dia chi)\s*[:\-]?\s*([a-z0-9\s\,\.\-]{10,150}?)(?=\s+(ma so thue|tax id|customer code|mst|so invoice no|ref no|tong))",
        text
    )
    if match_buyer_address:
        parsed["buyer_address"] = match_buyer_address.group(1).strip()

    # 💸 Total amount
    match_total = re.search(r"(total amount|cong tien hang.*?)\s*[:\-]?\s*([\d\.]+)", text)
    if match_total:
        parsed["total_amount"] = float(match_total.group(2).replace(".", ""))

    # 💰 VAT amount
    match_vat = re.search(r"(vat amount|tong cong tien thue)\s*[:\-]?\s*([\d\.]+)", text)
    if match_vat:
        parsed["vat_amount"] = float(match_vat.group(2).replace(".", ""))

    # 💳 Grand total
    match_grand = re.search(r"(grand total|tong cong tien thanh toan)\s*[:\-]?\s*([\d\.]+)", text)
    if match_grand:
        parsed["grand_total"] = float(match_grand.group(2).replace(".", ""))

    return parsed
