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

    match_date = re.search(r"ngay[^\d]{1,10}(\d{1,2})[^\d]{1,10}(\d{1,2})[^\d]{1,10}(\d{4})", text)
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

    match_seller_name = re.search(r"don vi ban[^a-z0-9]{0,10}:?\s*(cong ty.*?)\s*(dia chi|address|ma so thue)", text)
    if match_seller_name:
        parsed["seller_name"] = match_seller_name.group(1).strip().upper()[:255]

    match_seller_tax = re.search(r"ma so thue[^\d]{0,10}(\d{10})", text)
    if match_seller_tax:
        parsed["seller_tax"] = match_seller_tax.group(1)

    match_seller_addr = re.search(r"(address|dia chi)[^a-z0-9]{0,10}(.{10,300}?)(ma so thue|tax code|dien thoai|phone)", text)
    if match_seller_addr:
        parsed["seller_address"] = match_seller_addr.group(2).strip()[:255]

    match_buyer_name = re.search(r"(don vi|company)[^a-z0-9]{0,10}(cong ty[^\n\r]{5,120})", text)
    if match_buyer_name:
        parsed["buyer_name"] = match_buyer_name.group(2).strip().upper()[:255]

    match_buyer_tax = re.search(r"ma so thue[^\d]{0,10}(\d{10,})", text)
    if match_buyer_tax:
        parsed["buyer_tax"] = match_buyer_tax.group(1)

    match_buyer_address = re.search(r"(address|dia chi)[^a-z0-9]{0,10}(.{10,300}?)(hinh thuc thanh toan|currency|exchange rate)", text)
    if match_buyer_address:
        parsed["buyer_address"] = match_buyer_address.group(2).strip()[:255]

    match_totals = re.search(r"tien thanh toan[^\d]*(\d{1,3}(?:\.\d{3})+)[^\d]*(\d{1,3}(?:\.\d{3})+)[^\d]*(\d{1,3}(?:\.\d{3})+)", text)
    if match_totals:
        try:
            a, b, c = match_totals.groups()
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
