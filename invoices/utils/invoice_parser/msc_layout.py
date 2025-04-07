from datetime import datetime
import re

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
        "serial": "",
        "items": []
    }

    match_serial = re.search(r"1c\d{2}[a-z]+", text)
    if match_serial:
        parsed["serial"] = match_serial.group(0).upper()

    match_number = re.search(r"so[^\d]{0,5}(\d{6,})", text)
    if match_number:
        parsed["invoice_number"] = match_number.group(1)

    match_date = re.search(r"ngay (\d{1,2}) thang (\d{1,2}) nam (\d{4})", text)
    if match_date:
        day, month, year = match_date.groups()
        parsed["invoice_date"] = datetime(int(year), int(month), int(day)).date()

    match_seller = re.search(r"(cong ty.*?)\s+\(?seller\)?", text)
    if match_seller:
        parsed["seller_name"] = match_seller.group(1).strip()

    match_tax = re.search(r"(tax code|ma so thue)\)?[:\-]?\s*(\d{10})", text)
    if match_tax:
        parsed["seller_tax"] = match_tax.group(2).strip()

    match_addr = re.search(r"(address|dia chi)\)?[:\-]?\s*(.+?)(\(?tax code\)?|mst|dien thoai|email|website|fax)", text)
    if match_addr:
        parsed["seller_address"] = match_addr.group(2).strip()

    match_buyer = re.search(r"(customer|nguo[iy] mua|ben mua)\s*[:\-]?\s*(cong ty.*?)\s+(dia chi|address|ma so thue|tax id)", text)
    if match_buyer:
        parsed["buyer_name"] = match_buyer.group(2).strip()

    match_buyer_tax = re.search(r"(tax id|ma so thue)\s*[:\-]?\s*([\d\s]{10,})", text)
    if match_buyer_tax:
        parsed["buyer_tax"] = match_buyer_tax.group(2).replace(" ", "").strip()

    match_buyer_address = re.search(r"(dia chi|address)\s*[:\-]?\s*(.+?)(ma so thue|tax id|customer code)", text)
    if match_buyer_address:
        parsed["buyer_address"] = match_buyer_address.group(2).strip()

    match_total = re.search(r"tong cong tien thanh toan.*?(\d+[\.\d]*)", text)
    if match_total:
        parsed["grand_total"] = float(match_total.group(1).replace(".", ""))

    return parsed
