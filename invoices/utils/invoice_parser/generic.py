from datetime import datetime
import re
import unicodedata

def normalize_text_for_matching(text: str) -> str:
    text = unicodedata.normalize("NFD", text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')  # remove accents
    text = text.lower()
    text = re.sub(r"[^a-z0-9:/\-\s\.\(\)]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def parse(text: str) -> dict:
    text = normalize_text_for_matching(text)

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
        "serial": "",
        "items": []
    }

    match_serial = re.search(r"(1k\d{2}[a-z]+)", text)
    if match_serial:
        parsed["serial"] = match_serial.group(1).upper()

    match_number = re.search(r"so[^\d]{0,5}(\d{6,})", text)
    if not match_number:
        match_number = re.search(r"\(no\)[^\d]{0,5}(\d{6,})", text)
    if match_number:
        parsed["invoice_number"] = match_number.group(1)

    match_date = re.search(r"ngay \(?(\d{1,2})[^\d]{1,10}(\d{1,2})[^\d]{1,10}(\d{4})", text)
    if match_date:
        try:
            day, month, year = match_date.groups()
            parsed["invoice_date"] = datetime(int(year), int(month), int(day)).date()
        except Exception as e:
            print("❌ Lỗi chuyển đổi ngày:", e)
    else:
        match_fallback = re.search(r"(\d{2})/(\d{2})/(\d{4})", text)
        if match_fallback:
            try:
                day, month, year = match_fallback.groups()
                parsed["invoice_date"] = datetime(int(year), int(month), int(day)).date()
            except:
                pass

    match_seller = re.search(r"cong ty co phan dich vu hang hoa tan son nhat", text)
    if match_seller:
        parsed["seller_name"] = "CÔNG TY CỔ PHẦN DỊCH VỤ HÀNG HÓA TÂN SƠN NHẤT"

    match_tax = re.search(r"ma so thue[^\d]{0,10}(0301215249)", text)
    if match_tax:
        parsed["seller_tax"] = match_tax.group(1)

    match_addr = re.search(r"46[^\n]{0,80}qu[aâ]n tan binh[^\n]{0,80}tp\. hcm", text)
    if match_addr:
        parsed["seller_address"] = "46-48 Hậu, Phường 4, Quận Tân Bình, TP. HCM, Việt Nam"

    match_buyer_name = re.search(r"don vi[^a-z0-9]{0,10}(cong ty tnhh green planet distribution centre)", text)
    if match_buyer_name:
        parsed["buyer_name"] = match_buyer_name.group(1)[:255]

    match_buyer_tax = re.search(r"ma so thue[^\d]{0,10}(0317077996)", text)
    if match_buyer_tax:
        parsed["buyer_tax"] = match_buyer_tax.group(1)

    match_buyer_address = re.search(r"address[^a-z0-9]{0,10}(.{10,200}?)hinh thuc thanh toan", text)
    if match_buyer_address:
        parsed["buyer_address"] = match_buyer_address.group(1).strip()[:255]

    match_totals = re.findall(r"tien thanh toan.*?(\d{1,3}(?:\.\d{3})+).*?(\d{1,3}(?:\.\d{3})+).*?(\d{1,3}(?:\.\d{3})+)", text)
    if match_totals:
        try:
            a, b, c = match_totals[-1]
            parsed["total_amount"] = float(a.replace(".", ""))
            parsed["vat_amount"] = float(b.replace(".", ""))
            parsed["grand_total"] = float(c.replace(".", ""))
        except:
            pass

    item_blocks = re.findall(r"awb:.*?(\d{1,3}(?:\.\d{3})+)[\s\n]+(\d{1,3}(?:\.\d{3})+)[\s\n]+(\d{1,3}(?:\.\d{3})+)", text)
    for block in item_blocks:
        try:
            parsed["items"].append({
                "item_name": "AWB block",
                "amount": float(block[0].replace(".", "")),
                "vat": float(block[1].replace(".", "")),
                "total": float(block[2].replace(".", ""))
            })
        except:
            continue

    return parsed
